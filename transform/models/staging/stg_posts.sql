-- stg_posts: one row per post, lightly cleaned. No joins, no business logic.

with source as (

    select * from {{ source('mastodon', 'raw_posts') }}

),

cleaned as (

    select
        post_id,
        content_html,
        trim(regexp_replace(content_html, '<[^>]+>', ' ', 'g')) as content_text,
        created_at,
        language,
        instance,
        is_reblog,
        source_hashtag,
        tags,
        coalesce(cardinality(tags), 0) as tag_count,
        author_server,
        loaded_at

    from source

)

select * from cleaned
