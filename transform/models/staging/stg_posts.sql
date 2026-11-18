-- stg_posts: one row per post, lightly cleaned. No joins, no business logic.

with source as (

    select * from {{ source('mastodon', 'raw_posts') }}

),
cleaned as (
    select
        post_id,
        content_html,
        trim(
            regexp_replace(
                regexp_replace(content_html, '<[^>]+>', ' ', 'g'),
                    '\s+', ' ', 'g'
                    )
                ) as content_text, /**content with html tags removed**/
        trim(regexp_replace(
            regexp_replace(
                regexp_replace(content_html, '<[^>]+>', ' ', 'g'),
                '#\s*\w+', '', 'g'
            ),
            '\s+', ' ', 'g'
        )) as content_no_hashtags, /**content with hashtags removed**/
        created_at,
        language,
        instance,
        is_reblog,
        source_hashtag,
        tags,
        coalesce(cardinality(tags), 0) as tag_count, /**count of tags**/
        author_server,
        loaded_at
    from source
)
select * from cleaned
