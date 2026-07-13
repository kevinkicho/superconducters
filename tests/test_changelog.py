from superconductors.changelog import Commit, parse_git_log, read_commits, render_changelog


def test_parse_git_log_records():
    raw = "abc\x1fa1b2c3\x1f2026-07-13T10:00:00-07:00\x1fAda\x1fCompact pipeline\x1e"
    commits = parse_git_log(raw)
    assert commits == [
        Commit(
            sha="abc",
            short_sha="a1b2c3",
            authored_at="2026-07-13T10:00:00-07:00",
            author="Ada",
            subject="Compact pipeline",
        )
    ]


def test_render_changelog_groups_by_date():
    commits = [
        Commit("a", "aaa", "2026-07-13T10:00:00Z", "Ada", "First"),
        Commit("b", "bbb", "2026-07-13T09:00:00Z", "Lin", "Second"),
    ]
    rendered = render_changelog(commits)
    assert rendered.count("## 2026-07-13") == 1
    assert "`aaa` First" in rendered


def test_read_commits_uses_bounded_git_command():
    commands = []

    def runner(command):
        commands.append(command)
        return ""

    assert read_commits(limit=5, runner=runner) == []
    assert "-n5" in commands[0]


def test_non_positive_limit_skips_git():
    assert read_commits(limit=0, runner=lambda _: (_ for _ in ()).throw(AssertionError())) == []
