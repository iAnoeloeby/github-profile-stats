# GitHub Stats Transparent Visualization - Extended
### templated from [jstrieb/github-stats](https://github.com/jstrieb/github-stats)

> These SVGs are generated automatically by GitHub Actions  
> and published from the `output` branch.

<p align="center">
   <a href="https://github.com/iAnoeloeby/github-profile-stats/">
      <img src="https://raw.githubusercontent.com/iAnoeloeby/github-profile-stats/output/generated/overview.svg" />
      <img src="https://raw.githubusercontent.com/iAnoeloeby/github-profile-stats/output/generated/languages.svg" />
      <img src="https://raw.githubusercontent.com/iAnoeloeby/github-profile-stats/output/generated/activity_graph.svg" />
      <img src="https://raw.githubusercontent.com/iAnoeloeby/github-profile-stats/output/generated/recent_commits.svg" />
   </a>
</p>


> ⚠️ **Important note**  
> This repository is based on the original work by  
> **@jstrieb / github-stats** → https://github.com/jstrieb/github-stats  
>
> The original author owns the core idea and implementation.  
> This repo is a **personal extension** with additional logic, caching, and
> output-focused tweaks.

---

## 🧩 Usage guidance

If you want to use this project:

1. **Generate a new repository from the template**  
   Do **not** fork unless you want the full commit history.

2. **Star the original repository**  
   Please support the original author:  
   👉 https://github.com/jstrieb/github-stats ⭐

3. Modify freely  
   This repository is intentionally structured for customization.

---

## 🪐 What’s different in this version

This version keeps the original structure, but adds improvements focused on
**practical usage and maintainability**:

   - Incremental computation instead of full recomputation
   - Cached statistics for expensive operations
   - Recent commits and activity data generation
   - Output artifacts pushed to a dedicated branch
   - Clear handling of GitHub API limitations

This is **not a rewrite**, just a tuned version based on real usage.

---

## 🔑 Design notes (brief)

   - **Incremental over full scan**  
   First run scans everything, next runs only process new data.

   - **API-aware by design**  
   GitHub APIs have limits (Events API, delayed stats).  
   This repo works *with* those constraints, not against them.

   - **Output-first workflow**  
   Generated SVGs are treated as build artifacts and published from an
   `output` branch for easy embedding.

---

## 🛠 Example generated output

Assets are generated via **GitHub Actions** and served from the **output branch**:
> &ast; Replace ```<your-username>``` and ```<your-repo>``` accordingly.

```md
<!-- Overview -->
![](https://raw.githubusercontent.com/<your-username>/<your-repo>/output/generated/overview.svg)

<!-- Languages -->
![](https://raw.githubusercontent.com/<your-username>/<your-repo>/output/generated/languages.svg)

<!-- Recent Commits -->
![](https://raw.githubusercontent.com/<your-username>/<your-repo>/output/generated/recent_commits.svg)

<!-- Activity Graph -->
![](https://raw.githubusercontent.com/<your-username>/<your-repo>/output/generated/activity_graph.svg)
```

## 🧷 Related Projects

- Built on top of [jstrieb/github-stats](https://github.com/jstrieb/github-stats)

- Part of the wider GitHub stats ecosystem inspired by 
[anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats)

- Transparent theme ideas referenced from 
  [rahul-jha98/github-stats-transparent](https://github.com/rahul-jha98/github-stats-transparent)

- Uses 
  [GitHub Octicons](https://primer.style/octicons/) 
  to keep icons consistent with the GitHub UI
