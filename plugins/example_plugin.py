from plugins.genode_plugins_base import GenodePlugin
import dearpygui.dearpygui as dpg
import networkx as nx


#test_graphiz = False
test_graphiz = True

class ExamplePlugin(GenodePlugin):
    @staticmethod
    def name():
        return "Example"

    def __init__(self):
        self.app = None
        self.ne = None
        self.layout_types = {
                "Spring": nx.spring_layout,
                #"Bipartite": nx.bipartite_layout,
                "Circular": nx.circular_layout,
                "Kamada Kawai": nx.kamada_kawai_layout,
                "Planar": nx.planar_layout,
                #"Random": nx.random_layout,
                "Shell": nx.shell_layout,
                #"Spectral": nx.spectral_layout,
                #"Spiral": nx.spiral_layout,
                "Multipartite": nx.multipartite_layout}


        self.sel_layout = list(self.layout_types.keys())[-1]
        # Create a graph to demonstrate the node editor

        # Generate the computer network graph
        #self.G = nx.Graph()
        #self.G = nx.DiGraph()
        self.G = nx.MultiDiGraph()
        #self.G = nx.complete_multipartite_graph()

        #self.G.add_node("router", image=images["router"])
        #self.G.graph["rankdir"] = "TB"
        self.G.graph["rankdir"] = "LR"
        self.G.graph["ranksep"]= "5.0"
        #self.G.graph["rotate"] = "90"
        self.G.graph["ratio"] = "1.0"
        self.G.graph["nodesep"] = "0.5"
        self.G.graph["edgesep"] = "0.5"
        #self.G.graph["overlap"] = "false"
        self.G.add_node("router")
        self.G.nodes["router"]["subset"] = 0
        for i in range(1, 4):
            n = f"switch_{i}"
            #self.G.add_node(f"switch_{i}", image=images["switch"])
            self.G.add_node(n, shape="box", width=0.5, height=0.5)
            self.G.nodes[n]["subset"] = 1
            for j in range(1, 4):
                m = "PC_%d_%d" % (i, j)
                #self.G.add_node("PC_" + str(i) + "_" + str(j), image=images["PC"])
                self.G.add_node(m, shape="box", width=0.5, height=0.5)
                self.G.nodes[m]["subset"] = 2

        self.G.add_edge("router", "switch_1")
        self.G.add_edge("router", "switch_2")
        self.G.add_edge("router", "switch_3")

        self.graph_scale = 400
        self.graph_aspect_ratio = 0.3
        self.graph_center = [1 * self.graph_scale, 1 * self.graph_scale]

        self.prev_graph_scale = 400
        self.prev_graph_aspect_ratio = 0.3
        self.prev_graph_center = [1 * self.graph_scale, 1 * self.graph_scale]

        for u in range(1, 4):
            for v in range(1, 4):
                self.G.add_edge("switch_" + str(u), "PC_" + str(u) + "_" + str(v))

        if test_graphiz:
            self.pos = nx.nx_agraph.pygraphviz_layout(self.G, prog="dot", args="-y")
        else:
            self.pos = self.layout_types[self.sel_layout](G=self.G)
            self.pos = self.adjust_position(self.pos)








        print("pos:" % self.pos)
        print ("INFO: %s" %  str(nx.info(self.G)))
        #print ("Position Count: %d" % len(self.pos))

    def scale_callback(self, sender, app_data, user_data):
        self.graph_scale = app_data
        self.pos = self.invert_adjust_position(self.pos)
        self.pos = self.adjust_position(self.pos)
        self.prev_graph_scale = self.graph_scale
        self.set_node_position(self.pos)

    def aspect_ratio_callback(self, sender, app_data, user_data):
        print ("New Aspect Ratio: %f" % app_data)
        print ("PRE Pos: %s" % str(self.pos))
        self.graph_aspect_ratio = app_data
        self.pos = self.invert_adjust_position(self.pos)
        print ("INV Adj Pos: %s" % str(self.pos))
        self.pos = self.adjust_position(self.pos)
        print ("ADJ Pos: %s" % str(self.pos))
        self.prev_graph_aspect_ratio = self.graph_aspect_ratio
        self.set_node_position(self.pos)

    def center_x_callback(self, sender, app_data, user_data):
        self.graph_center[0] = app_data
        self.pos = self.invert_adjust_position(self.pos)
        self.pos = self.adjust_position(self.pos)
        self.prev_graph_center[0] = self.graph_center[0]
        self.set_node_position(self.pos)

    def center_y_callback(self, sender, app_data, user_data):
        self.graph_center[1] = app_data
        self.pos = self.invert_adjust_position(self.pos)
        self.pos = self.adjust_position(self.pos)
        self.prev_graph_center[1] = self.graph_center[1]
        self.set_node_position(self.pos)

    # callback runs when user attempts to connect attributes
    def link_callback(sender, app_data):
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    # callback runs when user attempts to disconnect attributes
    def delink_callback(sender, app_data):
        dpg.delete_item(app_data)

    def _log(sender, app_data, user_data):
        print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")

    def invert_adjust_position(self, pos):
        for p in pos:
            x = pos[p][0]
            y = pos[p][1]
            x = (x - self.prev_graph_center[0]) / (1.0 / self.prev_graph_aspect_ratio) / self.prev_graph_scale
            y = (y - self.prev_graph_center[1]) / (self.prev_graph_aspect_ratio)       / self.prev_graph_scale
            pos[p] = (x, y)
        return pos

    def adjust_position(self, pos):
        for p in pos:
            x = pos[p][0]
            y = pos[p][1]
            x = (x * self.graph_scale * (1.0 / self.graph_aspect_ratio)) + self.graph_center[0]
            y = (y * self.graph_scale * (self.graph_aspect_ratio)      ) + self.graph_center[1]
            pos[p] = (x, y)
        return pos

    def set_node_position(self, pos):
        #pos = self.adjust_position(pos)
        #print ("Pos: %s" % pos)

        if self.ne is not None:
            nodes = dpg.get_item_children(self.ne)[1]
            for n in self.G.nodes():
                dpg.set_item_pos(n, pos[n])

    def layout_select_changed(self, sender, app_data, user_data):
        print ("Layout changed")
        self.sel_layout = app_data
        self.pos = self.layout_types[self.sel_layout](G=self.G, center=self.graph_center, scale=self.graph_scale)
        self.set_node_position(self.pos)

    def start(self, app, parent):
        print ("Set all the nodes up")
        self.app = app
        hg = None
        self.ne = None


        control_width = 200
        with dpg.group(horizontal=True, parent=parent) as hg:
            with dpg.group(horizontal=False):
                with dpg.group(horizontal=True, width = control_width):
                    dpg.add_button(label="Start Graph",  callback=self._log, user_data="Start Graph", width=control_width / 2)
                    dpg.add_button(label="End Graph",    callback=self._log, user_data="End Graph", width=control_width / 2)

                dpg.add_listbox(items=list(self.layout_types.keys()), num_items=10, callback=self.layout_select_changed, width=control_width)
                dpg.add_input_float(label="scale", tag="scale_float", callback=self.scale_callback, width=control_width, default_value=self.graph_scale)
                dpg.add_input_float(label="aspect ratio", tag="aspect_ratio_float", callback=self.aspect_ratio_callback, width=control_width, default_value=self.graph_aspect_ratio)
                with dpg.group(horizontal=True, width = control_width):
                    dpg.add_input_float(label="center x", tag="center_x_float", callback=self.center_x_callback, width=control_width / 2, default_value=self.graph_center[0])
                    dpg.add_input_float(label="center y", tag="center_y_float", callback=self.center_y_callback, width=control_width / 2, default_value=self.graph_center[1])

            with dpg.node_editor(callback=self._log, delink_callback=self._log) as self.ne:
                pass

        rG = nx.reverse_view(self.G)

        for n in self.G.nodes():
            print ("Node: %s, Position: %s" % (n, self.pos[n]))
            with dpg.node(pos=self.pos[n], label=n, tag=n, parent=self.ne) as nd:
                if len(rG.edges(n)) > 0:
                    for e in rG.edges(n):
                        name = "%s_%s_in" % (e[1], e[0])
                        fname = "f_%s" % name
                        #print ("        Input Edge:  %s     %s" % (str(e), name))
                        with dpg.node_attribute(label=name, tag=name, attribute_type=dpg.mvNode_Attr_Input):
                            dpg.add_input_float(label=fname, width=100)

                if len(self.G.edges(n)) > 0:
                    for e in self.G.edges(n):
                        name = "%s_%s_out" % (e[0], e[1])
                        fname = "f_%s" % name
                        #print ("        Output Edge: %s     %s" % (str(e), name))
                        with dpg.node_attribute(label=name, tag=name, attribute_type=dpg.mvNode_Attr_Output) as nad:
                            print ("    nad: %s" % str(nad))
                            dpg.add_input_float(label=fname, width=100)


        for n in self.G.nodes():
            for e in self.G.edges(n):
                #print ("Edge: %s" % str(e))
                in_name = "%s_%s_in" % (e[0], e[1])
                out_name = "%s_%s_out" % (e[0], e[1])
                #print ("Edge: %s -> %s" % (out_name, in_name))
                dpg.add_node_link(out_name, in_name, parent=self.ne)



    def stop(self):
        print ("Tear down all the nodes")


