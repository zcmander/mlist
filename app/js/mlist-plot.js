Date.prototype.getWeek = function() {
    var determinedate = new Date();
    determinedate.setFullYear(this.getFullYear(), this.getMonth(), this.getDate());
    var D = determinedate.getDay();
    if(D == 0) D = 7;
    determinedate.setDate(determinedate.getDate() + (4 - D));
    var YN = determinedate.getFullYear();
    var ZBDoCY = Math.floor((determinedate.getTime() - new Date(YN, 0, 1, -6)) / 86400000);
    var WN = 1 + Math.floor(ZBDoCY / 7);
    return WN;
}

mlist.statistics = (function() {
    var medialist = null;

    // Sampled datasets
    var sampled_per_year = null;
    var sampled_per_month = null;
    var sampled_per_week = null;

    var exported_data = null;

    return {

    parse_csv_value: function (value, state) {
        if (state.colNum == 2) { // Date-column, 1-indexing
            var strDate = value;
            var dateParts = strDate.split(".");
            return new Date(dateParts[2], (dateParts[1] - 1), dateParts[0]);
        }
        return value;
    },

    create_sampled_datasets: function(data) {
        sampled_per_year = {};
        sampled_per_month = {};
        sampled_per_week = {};

        for (var i in data) {
            var mic = data[i];
            var date = new Date(mic.date);
            var year = date.getFullYear();
            var month = year + "-" + (date.getMonth()+1);
            var week = year + "-" + date.getWeek();

            if (!(year in sampled_per_year)) {
                sampled_per_year[year] = new Array();
            }

            if (!(month in sampled_per_month)) {
                sampled_per_month[month] = new Array();
            }

            if (!(week in sampled_per_week)) {
                sampled_per_week[week] = new Array();
            }

            sampled_per_year[year].push(mic);
            sampled_per_month[month].push(mic);
            sampled_per_week[week].push(mic);
        }

    },

    create_media_counts_dict: function (movielist) {
        var temp = {};

        for (var i in movielist) {
            var media = movielist[i].tags[0];

            if (!(media in temp)) {
                temp[media] = 1
            } else {
                temp[media] = temp[media] + 1;
            }
        }

        return temp
    },

    create_datatable_media_counts: function (movielist) {
        var temp = mlist.statistics.create_media_counts_dict(movielist)
        var result = new Array();
        for (var media in temp) {
            result.push([media, temp[media]])
        }
        return result;
    },

    create_datatable_for_historical_media: function (samplelist) {
        var temp = {};
        for (var group in samplelist) {
            temp[samplelist[group][0].date] = mlist.statistics.create_media_counts_dict(samplelist[group])
        }

        var result = new google.visualization.DataTable();
        result.addColumn('date', 'Watch date');

        for (var media in medialist) {
            result.addColumn("number", medialist[media])
        }

        var a = 0;
        for (var watch_date in temp) {
            result.addRows(1);
            result.setValue(a, 0, new Date(watch_date));

            for (var i in medialist) {
                var media = medialist[i];
                if (media in temp[watch_date]) {
                    result.setValue(parseInt(a), parseInt(i)+1, temp[watch_date][media]);
                } else {
                    result.setValue(parseInt(a), parseInt(i)+1, 0);
                }
            }

            //result.push(r);
            a += 1;
        }

        return result
    },

    create_datatable_for_watched_movies: function(samplelist) {
        var temp = [];
        for (var group in samplelist) {
            temp.push([group, samplelist[group].length, samplelist[group]]);
        }

        var result = new google.visualization.DataTable();
        result.addColumn('date', 'Watch date');
        result.addColumn('number', 'Count');

        result.addRows(temp.length);

        for (var i in temp) {
            result.setValue(parseInt(i), 0, new Date(temp[i][2][0].date));
            result.setValue(parseInt(i), 1, temp[i][1]);
        }
        return result
    },

    draw_watched_movies: function(sampledict) {
        var options = {
            height:"300",
            curveType: "function",
            chartArea: {
                width: '100%'
            },
            legend: {
                position: "none"
            },
            vAxis: {
                viewWindowMode: 'explicit',
                viewWindow: {
                    min: 0
                }
            },
            hAxis: {
                maxAlternation: 100,
                direction: 1
            },
        };
        var samplechooser = $("#chart-watched-movies").parent().find(".samplechooser");
        var samples = sampledict[samplechooser.find("button.active").html().toLowerCase()];
        var data = mlist.statistics.create_datatable_for_watched_movies(samples);
        var chart = new google.visualization.LineChart($('#chart-watched-movies')[0]);
        chart.draw(data, options);
    },

    draw_historical_media_distribution: function(sampledict) {
        var options = {
            height:"300",
            curveType: "function",
            chartArea: {
                width: '100%'
            },
            legend: {
                position: "none"
            },
            vAxis: {
                viewWindowMode: 'explicit',
                viewWindow: {
                    min: 0
                }
            },
            hAxis: {
                maxAlternation: 100,
                direction: 1
            }
        };
        var samplechooser = $("#chart-media-historical-distribution").parent().find(".samplechooser");
        var samples = sampledict[samplechooser.find("button.active").html().toLowerCase()];
        var data =  mlist.statistics.create_datatable_for_historical_media(samples);
        var chart = new google.visualization.LineChart($("#chart-media-historical-distribution")[0]);
        chart.draw(data, options);
    },

    draw_media_distribution: function(data) {
        var options = {
            chartArea: {
                width: '100%'
            },
            legend: {
                position: "none"
            },
        };
        var gdata = google.visualization.arrayToDataTable(
            [['Media', 'Count']].concat(mlist.statistics.create_datatable_media_counts(data))
        );
        var chart = new google.visualization.PieChart($('#chart-media-distribution')[0]);
        chart.draw(gdata, options);
    },

    draw_genre_distribution: function(data) {
        var options = {
            chartArea: {
                width: '100%'
            },
            legend: {
                position: "none"
            }
        };

        var genre_count = {
        };

        data.forEach(function(mic, index) {
            if (mic.movie.imdb == null) {
                return;
            }

            mic.movie.imdb.genres.forEach(function(genre) {
                if (genre in genre_count) {
                    genre_count[genre] += 1;
                } else {
                    genre_count[genre] = 1;
                }
            })
        });


        var result = [['Genre', 'Count']];

        for (var genre in genre_count) {
            result.push([genre, genre_count[genre]]);
        }

        var gdata = google.visualization.arrayToDataTable(result);

        var chart = new google.visualization.PieChart($('#chart-genre-distribution')[0]);
        chart.draw(gdata, options);
    },

    draw_watchdate_vs_releasedate: function(data) {
        function get_tooltip(mic) {
            return  "<b>" + mic.movie.title + "</b>" + "<br />Watched: " + new Date(mic.date).toLocaleDateString() + "<br />Release: " + new Date(mic.movie.imdb.released).toLocaleDateString()
        }

        var gdata = new google.visualization.DataTable();
        gdata.addColumn('date', 'Movie date');
        gdata.addColumn('date', 'Watch date');
        gdata.addColumn({type:'string',role:'tooltip','p': {'html': true}});

        gdata.addRows(data.length);

        var mic_index = null
        for (mic_index in data) {
            var mic = data[mic_index];
            if (mic.movie.imdb == null) {
                continue;
            }
            gdata.setValue(parseInt(mic_index), 0, new Date(mic.date));
            gdata.setValue(parseInt(mic_index), 1, new Date(mic.movie.imdb.released));
            gdata.setValue(parseInt(mic_index), 2, get_tooltip(mic));
        }

        var options = {
            chartArea: {
                width: '100%'
            },
            legend: 'none',
            height:"300",
            tooltip: {isHtml: true},
        };

        var chart = new google.visualization.ScatterChart(
                $("#chart-watchdate-vs-movieyear")[0]
        );
        chart.draw(gdata, options);
    },

    draw: function() {
        $(".js-results").fadeIn();

        var data = exported_data;

        medialist = new Array();
        for (var i in data) {
            var media = data[i].tags[0];
            if ($.inArray(media, medialist) == -1) {
                medialist.push(media);
            }
        }

        mlist.statistics.draw_media_distribution(data);
        mlist.statistics.draw_genre_distribution(data);
        mlist.statistics.draw_watchdate_vs_releasedate(data);

        mlist.statistics.create_sampled_datasets(data);
        mlist.statistics.updateView(data);
    },

    stats_show: function (e) {
        $(".js-loading").show();
        $.ajax({
            url: mlist.settings.urls.adv_export_movies,
            success: function(data) {
                exported_data = data;
                $(".js-loading").hide();
                mlist.statistics.draw();
            }
        });
    },

    updateView: function () {
        sampledict = {
            "year": sampled_per_year,
            "month": sampled_per_month,
            "week": sampled_per_week
        }
        this.draw_watched_movies(sampledict);
        this.draw_historical_media_distribution(sampledict);
    },

    init: function() {

        $(".samplechooser button").click(function(e) {
            $(this).parent(".samplechooser").find("button").removeClass("active");
            $(this).addClass("active");
            mlist.statistics.updateView();
        });

        mlist.statistics.stats_show();

        $(window).resize(function(){
            mlist.statistics.updateView();
            mlist.statistics.draw();
        });  
    }
};

})();
