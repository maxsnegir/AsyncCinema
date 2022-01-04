updated_genres = """
    SELECT id uuid, name, description, updated_at
    FROM content.genre
    WHERE updated_at > %s::timestamp
    ORDER BY updated_at
    """

updated_film_works = """
    SELECT fw.id uuid, fw.updated_at
    FROM content.film_work fw
    WHERE updated_at > %s::timestamp
    ORDER BY updated_at
    """

updated_persons = """
SELECT p.id uuid,
       p.full_name,
       p.birth_date, 
       p.updated_at,
       ARRAY_AGG(DISTINCT pfw.film_work_id)::text[] AS film_ids,
       ARRAY_AGG(DISTINCT pfw.role) AS role

    FROM content.person p 
    LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
    WHERE p.updated_at >  %s::timestamp
    GROUP BY p.id
    ORDER BY p.updated_at;
"""

film_work_data_by_ids = """
        SELECT DISTINCT fw.id uuid,
               fw.title title,
               fw.description description,
               fw.rating imdb_rating,
               fw.updated_at updated_at,

               ARRAY_AGG(DISTINCT jsonb_build_object('uuid', g.id, 'name', g.name)) AS genre,
               ARRAY_AGG(DISTINCT jsonb_build_object('uuid', p.id, 'full_name', p.full_name)) FILTER (WHERE pfw.role='director') directors,
               ARRAY_AGG(DISTINCT jsonb_build_object('uuid', p.id, 'full_name', p.full_name)) FILTER (WHERE pfw.role='actor') actors,
               ARRAY_AGG(DISTINCT jsonb_build_object('uuid', p.id, 'full_name', p.full_name)) FILTER (WHERE pfw.role='writer') writers

        FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw on fw.id=gfw.film_work_id 
            LEFT JOIN content.person_film_work pfw on fw.id=pfw.film_work_id
            LEFT JOIN content.genre g on gfw.genre_id=g.id
            LEFT JOIN content.person p on pfw.person_id=p.id
        WHERE fw.id in %s
        GROUP BY fw.id 
        ORDER BY fw.updated_at
        """

film_work_id_by_genre = """
        SELECT DISTINCT fw.id uuid
        FROM content.film_work fw
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        WHERE gfw.genre_id IN %s
        """

film_work_id_by_person = """
        SELECT fw.id uuid
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        WHERE pfw.person_id IN %s
        """


