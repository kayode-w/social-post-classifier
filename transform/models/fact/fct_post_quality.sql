{{ config(materialized='table') }}

with
posts as 
(
	select * 
	from {{ ref('stg_posts') }}
	where language = 'en'

),
quality_check as
(
	select 
	post_id, 
	source_hashtag,
	created_at,
	language,
	case 
		when is_reblog = False then True 
		else False
		end as is_original,
	case 
		when tag_count <= 8 then True
		else False
		end as is_not_stuffed,
    exists (
            select 1 
            from {{ ref('hashtag_keywords') }} k
            where k.hashtag = posts.source_hashtag /**two step look up - step 1: match on keyword e.g "fitness"**/
              and posts.content_no_hashtags ~* ('\m' || k.keyword || '\M') /**step 2: does the content contain any of the associated keywords?**/
        	) as is_on_topic
		
	from posts
)
select 
*,
case
	when is_original and is_not_stuffed and is_on_topic then true
	else false
	end as passed_quality_check
from quality_check