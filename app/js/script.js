/* Author: Teijo Mursu

*/


var ajaxManager = (function() {
     var requests = [];

     return {
        addReq:  function(opt) {
            requests.push(opt);
        },
        removeReq:  function(opt) {
            if( $.inArray(opt, requests) > -1 )
                requests.splice($.inArray(opt, requests), 1);
        },
        run: function() {
            var self = this,
                orgSuc;

            if( requests.length ) {
                oriSuc = requests[0].complete;

                requests[0].complete = function() {
                     if( typeof oriSuc === 'function' ) oriSuc();
                     requests.shift();
                     self.run.apply(self, []);
                };

                $.ajax(requests[0]);
            } else {
              self.tid = setTimeout(function() {
                 self.run.apply(self, []);
              }, 1000);
            }
        },
        stop:  function() {
            requests = [];
            clearTimeout(this.tid);
        }
     };
}());

var mlist = {
    settings: {},

    movie_title_typeahead: function (term, typeahead) {
        var searchData = null;
        $.getJSON("http://www.omdbapi.com/?callback=?&s=" + term + "&apikey=da2a56d7",
            function(data) {
                var result = [];
                var movie;
                for (i in data.Search) {
                    var movie = data.Search[i];
                    result.push({
                        'name':movie.Title + " (" + movie.Year + ")",
                        'imdb_id': movie.imdbID,
                        'year': movie.Year,
                        'title': movie.Title
                    });
                }
                typeahead(result);
                console.log(result)
            }
        );
    },

    handle_batch: function (e) {
        e.preventDefault();
        var target = $(this).attr("data-target");
        var results = $(".action-result");
        results.html("");
        $(this).attr("disabled", "disabled");

        for (current_target in g_handle_list[target]) {
            ajaxManager.addReq({
                url: g_handle_list[target][current_target],
                async: true,
                cache: false,
                context: {
                    url: g_handle_list[target][current_target]
                },
                success: function(data) {
                    var result = $("<li>").append("Handling " + this.url);
                    results.append(result);
                    result.append("OK");
                },
                error: function(xhr, status, errorThrown) {
                    var result = $("<li>").append("Handling " + this.url);
                    results.append(result);
                    result.append(
                            $("<div>").attr("class", "alert alert-danger").append(
                                    $("<strong>").append(status),
                                    "<br />",
                                    errorThrown
                            )
                    );
                }
            });
        }

        $(this).removeAttr("disabled");
    },

    init: function(settings) {
        mlist.settings = settings;

        $('.movie-title-typeahead').typeahead({
            source: mlist.movie_title_typeahead,
            afterSelect: function(obj) {
                $('.movie-title-typeahead').val(obj['title']);
                $('.movie-imdb_id-typeahead').val(obj['imdb_id']);
            }
        });

        ajaxManager.run();

        $(".handle-queries").click(mlist.handle_batch);

        if ($(".tagManager").length != 0) {
            $.get(mlist.settings.urls.tag_list).then((data) => {
                var input = $(".tagManager");
                input.tagsinput({
                    trimValue: true,
                    typeahead: {
                        source: data,
                    },
                });
                $(".bootstrap-tagsinput").find('input').addClass("form-control");
                input.on('itemAdded', function() {
                    $(".bootstrap-tagsinput").find('input').val('');
                  });
            });
        }
    },

    /* This 'hack' loads first image and then displays it as body's background image */
    change_background: function(settings) {
        var image = 'image.php',
        img = $('<img />');
        img.bind('load', function() {
            $("body").css("background-image", "url('" + settings.url + "')");
        });
        img.attr('src', settings.url);
    },
};

window.mlist = mlist;