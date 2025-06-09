import json
import re
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


def clean_text(text):
    # Remove broken Unicode surrogate characters
    return re.sub(r'[\ud800-\udfff]', '', text)


def process_posts(raw_file_path, processed_file_path=None):
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)

    enriched_posts = []
    for post in posts:
        try:
            cleaned_post = clean_text(post['text'])
            metadata = extract_metadata(cleaned_post)
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)
        except OutputParserException as e:
            print(f"Error processing post: {post['text'][:30]}... => {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {post['text'][:30]}... => {str(e)}")

    try:
        unified_tags = get_unified_tags(enriched_posts)
        for post in enriched_posts:
            current_tags = post.get('tags', [])
            new_tags = {unified_tags.get(tag, tag) for tag in current_tags}
            post['tags'] = list(new_tags)
    except Exception as e:
        print(f"Error unifying tags: {str(e)}")

    # Clean text before saving
    for post in enriched_posts:
        post['text'] = clean_text(post['text'])

    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4, ensure_ascii=False)

    print(f"✅ Processed posts saved to: {processed_file_path}")


def extract_metadata(post):
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)

    Here is the actual post on which you need to perform this task:
    {post}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post})

    try:
        json_parser = JsonOutputParser()
        return json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")


def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata:
        tags = post.get('tags', [])
        unique_tags.update(tags)

    unique_tags_list = ','.join(unique_tags)

    template = '''I will give you a list of tags. You need to unify tags with the following requirements:
    1. Tags are unified and merged to create a shorter list. 
    2. Each tag should follow title case convention.
    3. Output should be a JSON object mapping original to unified tags. No preamble.

    Here is the list of tags:
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": unique_tags_list})

    try:
        json_parser = JsonOutputParser()
        return json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse tags.")


if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")
