from mlist.omdbapi import BackendOMDB


def resolve_imdb_id_by_title(title):
    movie = BackendOMDB().get_data(title)

    if movie:
        return movie['imdb_id']
