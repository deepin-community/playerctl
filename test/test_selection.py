from .mpris import setup_mpris, setup_playerctld
from .playerctl import PlayerctlCli
import pytest
import asyncio


def selector(bus_address):
    playerctl = PlayerctlCli(bus_address)

    async def select(*players):
        assert players
        cmd = '-p ' + str.join(
            ',', players) + ' status --format "{{playerInstance}}"'
        result = await playerctl.run(cmd)
        assert result.returncode == 0, result.stderr
        return result.stdout

    async def select_many(*players):
        assert players
        cmd = '--all-players -p ' + str.join(
            ',', players) + ' status --format "{{playerInstance}}"'
        result = await playerctl.run(cmd)
        assert result.returncode == 0, result.stderr
        return tuple(result.stdout.split('\n'))

    return select, select_many


@pytest.mark.asyncio
async def test_selection(bus_address):
    s1 = 'selection1'
    s1i = 'selection1.i_123'
    s2 = 'selection2'
    s3 = 'selection3'
    m4 = 'selection4'
    m5 = 'selection5'
    m6 = 'selection6'
    s6i = 'selection6.i_2'
    any_player = '%any'

    mpris_players = await setup_mpris(s1,
                                      s1i,
                                      s2,
                                      s3,
                                      s6i,
                                      bus_address=bus_address)

    # TODO: test ignored players
    selections = {
        (s1, ): (s1, s1i),
        (s3, s1): (s3, s1, s1i),
        (s2, s1, s3): (s2, s1, s1i, s3),
        (s1, s2): (s1, s1i, s2),
        (m4, m5, s2, s3): (s2, s3),
        (m5, s1, m4, s3): (s1, s1i, s3),
        (s1, s1i): (s1, s1i),
        (s1i, s1): (s1i, s1),
        (m6, s1): (s6i, s1, s1i),
        (m4, m6, s3): (s6i, s3),
        (any_player, ): (s1, s1i, s2, s3, s6i),
        (s1, any_player): (s1, s1i, s2, s3, s6i),  # s1 first
        (any_player, s1): (s2, s3, s6i, s1, s1i),  # s1 last
        (m6, any_player, s2): (s6i, s1, s1i, s3, s2),  # s6 first, s2 last
        (m6, s1, any_player, s2): (s6i, s1, s1i, s3, s2),
    }

    select, select_many = selector(bus_address)

    for selection, expected in selections.items():
        result = await select(*selection)
        assert result == expected[0], (selection, expected, result)
        result = await select_many(*selection)
        assert result == expected

    await asyncio.gather(*[mpris.disconnect() for mpris in mpris_players])


@pytest.mark.asyncio
async def test_daemon_selection(bus_address):
    playerctld = await setup_playerctld(bus_address=bus_address)
    playerctl = PlayerctlCli(bus_address)

    def iface_name(player_name):
        return f'org.mpris.MediaPlayer2.{player_name}'

    def set_players(players):
        playerctld.player_names = [iface_name(p) for p in players]

    s1 = 'selection1'
    s1i = 'selection1.i_123'
    s2 = 'selection2'
    s2i = 'selection2.i_123'
    s3 = 'selection3'
    m4 = 'selection4'
    m5 = 'selection5'
    m6 = 'selection6'
    s6i = 'selection6.i_2'
    any_player = '%any'

    # selection, players, expected result
    all_players = [s1, s1i, s2, s3, s6i]
    tests = [
        (None, all_players, all_players),
        (all_players, all_players, all_players),
        ([s2], [s1, s2], [s2]),
        ([s1], [s2, s1i, s1], [s1i, s1]),
        ([s1], [s2, s1, s1i], [s1, s1i]),
        ([s1i, s1], [s1, s1i], [s1i, s1]),
        ([any_player], all_players, all_players),
        ([any_player, s1], [s1, s1i, s2i, s2], [s2i, s2, s1, s1i]),
        ([any_player, s1], [s1, s1i, s2, s2i], [s2, s2i, s1, s1i]),
        ([any_player, s1], [s1i, s1, s2i, s2], [s2i, s2, s1i, s1]),
        ([any_player, s1], [s1i, s1, s2, s2i], [s2, s2i, s1i, s1]),
        ([s2, any_player], [s1, s1i, s2i, s2], [s2i, s2, s1, s1i]),
        ([s2, any_player], [s1, s1i, s2, s2i], [s2, s2i, s1, s1i]),
        ([s2, any_player], [s1i, s1, s2i, s2], [s2i, s2, s1i, s1]),
        ([s2, any_player], [s1i, s1, s2, s2i], [s2, s2i, s1i, s1]),
        ([s2i, any_player], [s1i, s1, s2, s2i], [s2i, s1i, s1, s2]),
    ]

    async def daemon_selection_test(test):
        selection, players, expected = test
        set_players(players)
        result = await playerctl.list(players=selection)
        assert result == expected, test

    for test in tests:
        # unfortunately it won't work in parallel because there's only one
        # playerctld
        await daemon_selection_test(test)

    await playerctld.disconnect()
