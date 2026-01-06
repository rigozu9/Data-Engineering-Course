{% set rating_category = 'Excellent' %}

SELECT *
FROM {{ ref('film_ratings') }}
WHERE rating_category = '{{ rating_category }}'