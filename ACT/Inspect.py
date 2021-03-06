"""
This script will load in a .dot file and a .log file
generated by hacdump.sh and visualize the state-transition
"""
class __dot_defs__():
    PROGRAM = 'neato'
    ARGS = '-Goverlap=prism -Gsep=1'

class __networkx_defs__():
    NODE_LABEL_Y_OFFSET = -35
    NODE_SIZE = 200

class __disp_defs__():
    PATCH_RADIUS = 25
    PATCH_COLOR = 'g'
    PATCH_MIN_ALPHA = 0.1
    PATCH_ALPHA_DECAY = 0.075
    NODE_TEXT_X_OFFSET = -5
    NODE_TEXT_Y_OFFSET = -7
    TIME_MULTIPLIER = 0.1
    FIGSIZE = (9, 9)

def __draw_state_nodes__(dot_file):
    """
    Read in a .dot file, draw the nodes and return their positions
    """
    import networkx as nx
    import pygraphviz as pyg
    from matplotlib.pyplot import gca, draw, gcf

    gpy = pyg.AGraph(dot_file)
    gpy.layout(prog=__dot_defs__.PROGRAM, args=__dot_defs__.ARGS)
    pos = dict()
    pos_labels = dict()
    for nod in gpy.nodes_iter():
        _pos = nod.attr[u'pos'].split(',')
        _name = nod.name
        _pos = map(float, _pos)
        _pos_label = map(float, _pos)
        _pos_label[1] += __networkx_defs__.NODE_LABEL_Y_OFFSET
        pos[str(_name)] = tuple(_pos)
        pos_labels[str(_name)] = tuple(_pos_label)

    gnx = nx.read_dot(dot_file)
    node_labels = {str(n[0]):str(n[1]['label'])
                   for n in gnx.node.items()}
    nx.draw_networkx(gnx, pos=pos, with_labels=False,
                     node_color='w', node_size=__networkx_defs__.NODE_SIZE)
    nx.draw_networkx_labels(gnx, labels=node_labels, pos=pos_labels)

    current_ax = gca()
    current_ax.spines['top'].set_visible(False)
    current_ax.spines['right'].set_visible(False)
    current_ax.spines['bottom'].set_visible(False)
    current_ax.spines['left'].set_visible(False)
    current_ax.xaxis.set_ticks([])
    current_ax.yaxis.set_ticks([])
    gcf().set_tight_layout(True)
    draw()
    return pos

def __gen_tran__(log_file):
    """
    Read in a .log file, return event-transition table
    """
    import numpy as np
    tran_dt = np.dtype([('e_idx', np.uint), ('e_t', np.float), 
                        ('e_n', np.uint), ('c_idx', np.uint)])
    tran_list = np.loadtxt(log_file, dtype=tran_dt, skiprows=0)
    return tran_list

def __gen_states__(log_file):
    """
    Read in a .log file, return state-transition table
    """
    import numpy as np
    state_dt = np.dtype([('e_idx', np.uint), 
                        ('n_idx', np.uint), ('n_val', np.uint)])
    state_list = np.loadtxt(log_file, dtype=state_dt, skiprows=0)
    return state_list

def __generate_tran_nodes__(pos):
    """
    Generate a list of patches to match the node positions.
    """
    from matplotlib.patches import Circle
    from matplotlib.text import Text
    node_patches = dict()
    node_text = dict()
    num_nodes = len(pos)
    for node_idx in range(num_nodes):
        evt_idx = "EVENT_" + str(node_idx)
        node_pos = pos[evt_idx]
        node_patches[node_idx] = \
            Circle(xy=node_pos,
                   radius=__disp_defs__.PATCH_RADIUS,
                   color=__disp_defs__.PATCH_COLOR,
                   alpha=__disp_defs__.PATCH_MIN_ALPHA)
        node_text[node_idx] = \
            Text(x=node_pos[0] + __disp_defs__.NODE_TEXT_X_OFFSET,
                 y=node_pos[1] + __disp_defs__.NODE_TEXT_Y_OFFSET,
                 text='-1')
    return node_patches, node_text

def __draw_state_transition__(tran_list, state_list, node_map, node_patches, node_text, cur_ax, time_mult=0.1):
    """
    Draw the state transition
    """
    import time
    from numpy import zeros
    from matplotlib.pyplot import draw
    from matplotlib.table import Table

    num_tran = tran_list.shape[0]
    evt_id_list = tran_list['e_idx']
    evt_t_list = tran_list['e_t']
    evt_s_list = tran_list['e_n']

    state_e_list = state_list['e_idx']
    state_n_list = state_list['n_idx']
    state_val_list = state_list['n_val']

    len_states = len(state_e_list)

    x_lim = cur_ax.get_xlim()
    y_lim = cur_ax.get_ylim()
    x_range = x_lim[1] - x_lim[0]
    y_range = y_lim[1] - y_lim[0]
    col_width = x_range / float(len(node_map))
    row_height = y_range * 0.1 / 2.0
    state_table = Table(cur_ax, bbox=(0, 0, 1, 0.1))
    cell_pos = dict()
    for idx, key_value in enumerate(node_map.items()):
        _key = key_value[0]
        _val = key_value[1]
        cell_pos[_key] = idx
        state_table.add_cell(0, idx, col_width, row_height, 
                             text=str(_val), loc='center',
                             edgecolor='none', facecolor='none')
        state_table.add_cell(1, idx, col_width, row_height, 
                             text='-', loc='center',
                             edgecolor='none', facecolor='none')
    cur_ax.add_table(state_table)
    draw()
    state_cells = state_table.get_celld()

    t_delta_last = 0.0
    evt_mask = zeros(len(node_patches), dtype=int)
    patch_list = node_patches.values()
    last_time = -1.0
    new_state_idx = 0
    new_state_e = state_e_list[new_state_idx]
    for idx in range(num_tran):
        evt_id = evt_id_list[idx]
        evt_t = evt_t_list[idx]
        if last_time < evt_t:
            draw()
            for pat in patch_list:
                _alpha = pat.get_alpha()
                if _alpha > (__disp_defs__.PATCH_MIN_ALPHA +
                             __disp_defs__.PATCH_ALPHA_DECAY):
                    pat.set_alpha(_alpha - __disp_defs__.PATCH_ALPHA_DECAY)
            t_delta = evt_t - t_delta_last
            t_delta_last = evt_t
            time.sleep(t_delta * time_mult)
            last_time = evt_t
        evt_s = evt_s_list[idx]
        current_iter = evt_mask[evt_s]
        current_patch = node_patches[evt_s]
        current_patch.set_alpha(1.0)
        current_node_text = node_text[evt_s]
        current_node_text.set_text(current_iter)
        if current_patch.get_axes() is None:
            cur_ax.add_patch(current_patch)
            cur_ax.add_artist(current_node_text)
        current_iter += 1
        evt_mask[evt_s] = current_iter

        if evt_id == new_state_e:
            node_idx = state_n_list[new_state_idx]
            node_val = state_val_list[new_state_idx]
            cell_idx = cell_pos[node_idx]
            state_cells[(1, cell_idx)].get_text().set_text(str(node_val))
            print("t=%g, node: %s, val: %s" % (evt_t, node_map[node_idx], node_val))
            new_state_idx += 1
            if new_state_idx < len_states:
                new_state_e = state_e_list[new_state_idx]
            else:
                break

def ShowStateTransition(dot_file, event_log_file, state_log_file, node_map_file):
    """
    Take a dot file and log file and animate the state transition
    """
    from matplotlib.pyplot import gca, figure
    from numpy import genfromtxt

    time_mult = __disp_defs__.TIME_MULTIPLIER
    figure(figsize=__disp_defs__.FIGSIZE)
    pos = __draw_state_nodes__(dot_file)
    tran_list = __gen_tran__(event_log_file)
    state_list = __gen_states__(state_log_file)
    node_map = dict(genfromtxt(node_map_file, dtype=None))
    node_patches, node_text = __generate_tran_nodes__(pos)
    current_ax = gca()
    __draw_state_transition__(tran_list, state_list, node_map, node_patches, node_text,
                              current_ax, time_mult)
