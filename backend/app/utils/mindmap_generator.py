import json
import os
from graphviz import Digraph


def escape_label(text):
    return text.replace("<", "&lt;").replace(">", "&gt;").replace('"', '\\"')


def generate_mindmap(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = "backend/data/mindmaps"
    os.makedirs(output_dir, exist_ok=True)

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dot = Digraph(comment=f"Mindmap: {data['central_topic']}", format='png')
    dot.attr(rankdir='LR', bgcolor='white')
    dot.attr('node', shape='box', style='filled', fillcolor='#f0f8ff', fontsize='10', fontname="Arial")

    def add_subtopics(parent_id, subtopics, count):
        for i, topic in enumerate(subtopics):
            node_id = f"{parent_id}_{count[0]}"
            count[0] += 1
            title = escape_label(topic['title'])
            desc = escape_label(topic.get('description', ''))
            label = f"<<b>{title}</b><br/><font point-size='9'>{desc}</font>>"
            dot.node(node_id, label=label)
            dot.edge(parent_id, node_id)
            if 'children' in topic:
                add_subtopics(node_id, topic['children'], count)

    # Add central node
    central_id = "central"
    dot.node(central_id, f"<<b>{escape_label(data['central_topic'])}</b>>", shape='ellipse', fillcolor="#ffebcd", fontsize='13', fontname="Arial")

    # Add subtopics recursively
    add_subtopics(central_id, data['subtopics'], count=[1])

    # Save and render
    base_name = base_name.replace(" ", "-")
    dot.render(filename=base_name, directory=output_dir, cleanup=True)
    print(f"Mindmap saved to: {os.path.join(output_dir, base_name)}.png")
    return dot
