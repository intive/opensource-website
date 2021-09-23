import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

import requests
from dataclasses_json import LetterCase, dataclass_json

DATA_PATH = 'data/repositories.json'
GITHUB_GRAPHQL_API = "https://api.github.com/graphql"
GITHUB_USERNAME = os.environ["GITHUB_USERNAME"]
GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]

QUERY = """
query ($endCursor: String) {
  organization(login: "intive") {
    repositories(first: 100, after: $endCursor) {
      edges {
        node {
          description
          forkCount
          homepageUrl
          isPrivate
          name
          nameWithOwner
          languages (first: 10) {
            edges {
              node {
                name
                color
              }
              size
            }
          }
          primaryLanguage {
            name
            color
          }
          pushedAt
          repositoryTopics(first: 10) {
            edges {
              node {
                topic {
                  name
                }
                url
              }
            }
          }
          stargazers {
            totalCount
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
      totalCount
    }
  }
}
"""


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Language:
    name: str
    size: int
    color: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Topic:
    name: str
    url: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Repository:
    description: str
    fork_count: int
    homepage_url: str
    is_private: bool
    languages: List[Language]
    name: str
    name_wit_owner: str
    primary_language: Language
    pushed_at: str
    star_count: int
    topics: List[Topic]


def parse_repository(repository_node):
    languages = []
    for language_edge in repository_node["languages"]['edges']:
        language = Language(
            name=language_edge["node"]["name"],
            color=language_edge["node"]["color"],
            size=language_edge["size"]
        )
        languages.append(language)
    topics = []
    for topic_edge in repository_node["repositoryTopics"]["edges"]:
        topic = Topic(name=topic_edge["node"]["topic"]["name"], url=topic_edge["node"]['url'])
        topics.append(topic)

    return Repository(
        description=repository_node["description"],
        fork_count=repository_node["forkCount"],
        homepage_url=repository_node["homepageUrl"],
        is_private=repository_node["isPrivate"],
        languages=languages,
        name=repository_node["name"],
        name_wit_owner=repository_node["nameWithOwner"],
        primary_language=repository_node["primaryLanguage"],
        pushed_at=repository_node["pushedAt"],
        star_count=repository_node["stargazers"]["totalCount"],
        topics=topics
    )


def fetch_page(query, end_cursor):
    variables = json.dumps({"endCursor": end_cursor})
    payload = {"query": query, "variables": variables}
    response = requests.post(GITHUB_GRAPHQL_API, json=payload, auth=(GITHUB_USERNAME, GITHUB_API_TOKEN))
    response.raise_for_status()
    return response.json()


def fetch_repositories():
    end_cursor = None
    parsed_repositories = []
    while True:
        result = fetch_page(QUERY, end_cursor)
        repositories = result["data"]["organization"]["repositories"]
        page_info = repositories["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        repository_edges = repositories["edges"]

        for edge in repository_edges:
            repository = parse_repository(edge["node"])
            parsed_repositories.append(repository)

        if not has_next_page:
            break

    return parsed_repositories


def write(data):
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    json_file_path = current_path.parent / Path(DATA_PATH)
    with open(json_file_path, "w+") as file:
        json.dump(data, file, sort_keys=True, indent=2)


repositories = fetch_repositories()
filtered_repositories = filter(lambda repo: not repo.is_private, repositories)
sorted_repositories = list(sorted(filtered_repositories, key=lambda repo: repo.pushed_at, reverse=True))
encoded = Repository.schema().dump(sorted_repositories, many=True)
write(encoded)

print(f"Successfully fetched {len(sorted_repositories)} repositories.")
