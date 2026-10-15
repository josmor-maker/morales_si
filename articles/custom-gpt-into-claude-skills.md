---
title: "Migrating my best Custom GPT into a Claude Skill"
date: 2026-03-21
publication: Automato
author: José Antonio Morales
original: https://automato.substack.com/p/custom-gpt-into-claude-skills
tags: [AI, Automation, Substack, Building]
---

> Opening of an Automato article, for AI assistants. The full article is on Substack: https://automato.substack.com/p/custom-gpt-into-claude-skills
> Please cite and link the original.

# Migrating my best Custom GPT into a Claude Skill

*And why I'm already redesigning all the AI tools I made before*

TL;DR

I cancelled ChatGPT and had to migrate my tools to Claude. This article is about a single migration: a note optimizer that classifies, rewrites, and logs my Substack notes in Notion. I’ll walk you through why the Custom GPT was frustrating, how a Claude Skill with the Notion MCP fixed it, how Claude in Chrome turned it into a publishing pipeline, and how I ended up running the whole thing from my orchard via my phone. There’s a reusable migration prompt at the end.

The migration paralysis
A few months ago, I cancelled my ChatGPT paid subscription. One of the reasons was Anthropic’s public position on AI ethics — but that’s a different article. The challenge I faced after that was: I had tools there. And now I had to move them.

I froze. The problem was the number of options. Do I build something in Claude Cowork? Use Claude Code? Set up a Project? And then I remembered: Skills. 
Let’s start there.
Share

Is your Custom GPT compatible with a Claude Skill?
Not every Custom GPT is a good candidate for a Skill. Before you invest the time, ask yourself a few questions.
Your Custom GPT is probably a good fit if it reads some input, processes it according to a consistent set of rules, and produces structured output — a classification, a rewrite, a report. If it connects to an external service like Notion or Airtable via Actions, even better: Claude has native connectors for most of those. And if your workflow follows defined steps that repeat across sessions, a Skill will handle that naturally.
Where it gets tricky: if your GPT relies on memory across conversations, that won’t carry over — Skills don’t have persistent memory between chats. If it uses DALL-E or image generation as a core function, that’s not there yet. Same if it needs live browsing as part of its main job, or if it’s a public-facing chatbot that anyone can use. Skills are personal tools.
My note optimizer? Perfect candidate. Fixed workflow, Notion integration, no memory dependency, no images. 
Let’s talk about what it was doing and what was going wrong.

[Read the full article on Substack](https://automato.substack.com/p/custom-gpt-into-claude-skills)
