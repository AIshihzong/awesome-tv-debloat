# Contributing / 参与贡献

Thanks for helping. The fastest way is to [open an issue](https://github.com/AIshihzong/awesome-tv-debloat/issues/new?template=project.yml) with the repository link; a maintainer will read its README and add it.

## What gets in

- Open source, with the code on GitHub, GitLab or Codeberg.
- It removes ads, bloat or tracking from a TV, or replaces the TV's home screen, or blocks TV ads on the network.
- Its README says how to undo the change. Projects that only uninstall system apps, with no way back, are not listed.
- Not accepted: IPTV playlists or live-channel sources, paid-channel access, piracy add-ons, APK mirror sites, closed-source tools.

## Sending a pull request

1. Add one object to `projects` in [`data/projects.json`](data/projects.json): `s` (section id), `repo`, `name`, `root` (`no`, `dev`, `yes`), `setup` (`pc`, `phone`, `tv`, `router`, comma-separated), `agent` (true if it ships a prompt or skill for a coding agent), `undo` (`yes`, `partial`, `n/a`), and a one-line `en` and `zh` description.
2. Base the Root, Set up from and Undo fields on the project's README, and say where in your PR description.
3. Run `python3 scripts/build.py` to regenerate both READMEs. Do not edit the tables by hand; CI checks they match the data.
4. Keep descriptions factual: what it does and what it needs. No "best" or "ultimate".

中文贡献者：流程相同。描述请同时写 `en` 和 `zh`，中文用自然的说法，不要机翻。

## Corrections

If a project changes (for example it now needs root, or the undo script was removed), open an issue with a link to the line in its README. Wrong information about root or undo is fixed first.
