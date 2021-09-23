# Intive opensource website
This project is used to create the intive opensource website hosted at [opensource.intive.com](https://opensource.intive.com). 

## Repository list
The website presents among other things a list of all public repositories present in the intive organization.
The data is retrieved using githubs GraphQL API and stored into JSON under `data/repositories.json`.
To run this locally you can use the script `scripts/fetch_repositories.py`.
Make sure you have set the environment variable `GITHUB_API_TOKEN` when running:
```
python scripts/fetch_repositories.py
```
This step is automated using the `Fetch repositories` github workflow.

## Static site generation
The website is built using the static site generator [hugo](https://gohugo.io).
We use the great [coder template](https://github.com/luizdepra/hugo-coder) as a basis.

To build the page use the hugo cli.
```
hugo
```
The deployment of the site is done using the `Deploy` github workflow.
This will build the site and push the generated website to the `gh-pages` branch.

