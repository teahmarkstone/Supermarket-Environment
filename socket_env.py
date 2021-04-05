# Author: Gyan Tatiya
# Email: Gyan.Tatiya@tufts.edu
import argparse
import json
import socket
import time

from env import SupermarketEnv
from norms.norm import NormWrapper
from norms.norms import *
from utils import recv_socket_data

ACTION_COMMANDS = ['NOP', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'INTERACT', 'TOGGLE_CART', 'CANCEL']


# def get_goal(env_):
#     goal = {'goalType': 'ITEM'}
#     if env_.last_done:
#         goal['goalAchieved'] = True
#     else:
#         goal['goalAchieved'] = False
#
#     return goal


def get_action_json(action, env_, obs, reward, done, info_=None):
    # cmd, arg = get_command_argument(action)

    if not isinstance(info_, dict):
        result = True
        message = ''
        step_cost = 0
    else:
        result, step_cost, message = info_['result'], info_['step_cost'], info_['message']

    result = 'SUCCESS' if result else 'FAIL'

    action_json = {'command_result': {'command': action, 'result': result, 'message': message,
                                      'stepCost': step_cost},
                   'observation': obs,
                   'step': env_.step_count,
                   'gameOver': done}
    # print(action_json)
    # action_json = {"hello": "world"}
    return action_json


def is_single_player(command_):
    return ',' not in command_


def get_player_and_command(command_):
    split_command = command_.split(' ')
    if len(split_command) == 1:
        return 0, split_command[0]
    return split_command[0], split_command[1]


def get_commands(command_):
    split_command = [cmd.strip() for cmd in command_.split(',')]
    return split_command


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--num_players',
        type=int,
        help="location of the initial state to read in",
        default=1
    )

    parser.add_argument(
        '--port',
        type=int,
        help="Which port to bind",
        default=9000
    )

    parser.add_argument(
        '--headless',
        action='store_true'
    )

    parser.add_argument(
        '--file',
        help="location of the initial state to read in",
        default=None
    )

    parser.add_argument(
        '--follow',
        help="which agent to follow",
        type=int,
        default=-1
    )

    args = parser.parse_args()

    # np.random.seed(0)

    # Make the env
    # env_id = 'Supermarket-v0'  # NovelGridworld-v6, NovelGridworld-Pogostick-v0, NovelGridworld-Bow-v0
    # env = gym.make(env_id)
    env = SupermarketEnv(args.num_players, render_messages=False, headless=args.headless,
                         initial_state_filename=args.file,
                         follow_player=args.follow if args.num_players > 1 else 0
                         )

    norms = [CartTheftNorm(),
             WrongShelfNorm(),
             ShopliftingNorm(),
             PlayerCollisionNorm(),
             ObjectCollisionNorm(),
             WallCollisionNorm(),
             BlockingExitNorm(),
             EntranceOnlyNorm(),
             UnattendedCartNorm(),
             OneCartOnlyNorm(),
             PersonalSpaceNorm(dist_threshold=1),
             InteractionCancellationNorm(),
             ]

    env = NormWrapper(env, norms)
    # env.map_size = 32

    # Connect to agent
    HOST = '127.0.0.1'
    PORT = args.port
    sock_agent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_agent.bind((HOST, PORT))
    sock_agent.listen()
    conn_agent, addr = sock_agent.accept()
    print('Connected with agent: ', addr)

    TRIALS = 1
    MAX_STEPS = 1000

    for trial_num in range(1, TRIALS + 1):

        env.reset()
        start_time = time.time()
        step_count = 0
        planning_time = 0
        done = False
        while not done:
            # get command from agent
            try:
                output = recv_socket_data(conn_agent)
                command = output.decode().strip()
                if command.startswith("SET"):
                    obs = command[4:]
                    from json import loads

                    env.reset(obs=loads(obs))
                if is_single_player(command):
                    player, command = get_player_and_command(command)
                    player = int(player)

                    action = [0] * env.num_players
                    if command in ACTION_COMMANDS:
                        action_id = ACTION_COMMANDS.index(command)
                        action[player] = action_id
                        # print(action)
                        obs, reward, done, info = env.step(tuple(action))
                        json_to_send = get_action_json(command, env, obs, reward, done, info)
                    else:
                        info = {'result': False, 'step_cost': 0.0, 'message': 'Invalid Command'}
                        json_to_send = get_action_json(command, env, None, 0., False, info)
                else:
                    commands = get_commands(command)
                    valid = all(cmd in ACTION_COMMANDS for cmd in commands)
                    if valid:
                        action = tuple(ACTION_COMMANDS.index(cmd) for cmd in commands)
                        # print(action)
                        obs, reward, done, info = env.step(tuple(action))
                        json_to_send = get_action_json(command, env, obs, reward, done, info)
                    else:
                        info = {'result': False, 'step_cost': 0.0, 'message': 'Invalid Command'}
                        json_to_send = get_action_json(command, env, None, 0., False, info)
                # send JSON to agent
                conn_agent.sendall(str.encode(json.dumps(json_to_send) + "\n"))
                env.render()
            except (OSError, ValueError):
                sock_agent.close()

            step_count += 1
        sock_agent.close()
