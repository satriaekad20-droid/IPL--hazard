from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Instruction:
    name: str
    destination: str
    sources: list


instructions = [
    Instruction("I1", "R1", ["R2", "R3"]),
    Instruction("I2", "R4", ["R1", "R5"]),   # baca R1 yang ditulis I1
    Instruction("I3", "R6", ["R4", "R7"]),   # baca R4 yang ditulis I2
    Instruction("I4", "R8", ["R9", "R10"]),  # independen
]


def fmt(inst):
    return f"{inst.name}: {inst.destination} = {' + '.join(inst.sources)}"


def has_dependency(inst1, inst2):
    """True jika inst2 punya hazard RAW terhadap inst1 (inst1 lebih dulu)."""
    return inst1.destination in inst2.sources


def find_dependencies(instructions):
    deps = []
    for i in range(len(instructions)):
        for j in range(i + 1, len(instructions)):
            if has_dependency(instructions[i], instructions[j]):
                deps.append((instructions[i], instructions[j]))
    return deps


def show_dependencies(instructions):
    print("\n" + "=" * 50)
    print("DEPENDENCY ANALYSIS (RAW)")
    print("=" * 50)

    deps = find_dependencies(instructions)
    if not deps:
        print("No dependencies found.")
    for a, b in deps:
        print(f"{b.name} depends on {a.name} (Register: {a.destination})")
    return deps


def sequential_execution(instructions):
    print("\n" + "=" * 50)
    print("SEQUENTIAL EXECUTION")
    print("=" * 50)

    for cycle, inst in enumerate(instructions, start=1):
        print(f"Cycle {cycle}: {fmt(inst)}")

    print(f"\nTotal Sequential Cycles: {len(instructions)}")
    return len(instructions)


def parallel_execution(instructions):
    print("\n" + "=" * 50)
    print("INSTRUCTION-LEVEL PARALLEL EXECUTION")
    print("=" * 50)

    completed = set()
    remaining = instructions.copy()
    cycle = 0

    while remaining:
        cycle += 1
        current = []

        for inst in remaining:
            ready = True
            for prev in instructions:
                if prev.name == inst.name:
                    break
                if has_dependency(prev, inst) and prev.name not in completed:
                    ready = False
                    break
            if ready:
                current.append(inst)

        print(f"\nCycle {cycle}:")
        for inst in current:
            print(f"  -> {fmt(inst)}")

        for inst in current:
            completed.add(inst.name)
            remaining.remove(inst)

    print(f"\nTotal ILP Cycles: {cycle}")
    return cycle


def draw_dependency_graph(instructions, filename="graph_raw.png"):
    G = nx.DiGraph()
    for inst in instructions:
        G.add_node(inst.name)
    for a, b in find_dependencies(instructions):
        G.add_edge(a.name, b.name, reg=a.destination)

    pos = {inst.name: (i * 2, (i % 2) * 0.6) for i, inst in enumerate(instructions)}

    fig, ax = plt.subplots(figsize=(2.2 * len(instructions) + 2, 4))
    nx.draw_networkx_nodes(G, pos, node_size=1600, node_color="#f2f2f2",
                           edgecolors="black", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, ax=ax)

    for u, v, d in G.edges(data=True):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color="tab:red",
                               arrows=True, arrowsize=20, width=2, node_size=1600,
                               connectionstyle="arc3,rad=0.25", ax=ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f"RAW ({d['reg']})"},
                                     font_color="tab:red", font_size=9,
                                     connectionstyle="arc3,rad=0.25", ax=ax,
                                     bbox=dict(alpha=0))

    ax.text(0.0, -0.05, "\n".join(fmt(i) for i in instructions),
            transform=ax.transAxes, va="top", family="monospace", fontsize=9)
    ax.set_title("Dependency Graph - RAW")
    ax.axis("off")
    ax.margins(0.15)
    fig.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"\nSaved graph: {filename}")
    plt.show()
    plt.close(fig)


def main():
    print("*" * 60)
    print("      ILP SIMULATOR - RAW")
    print("*" * 60)

    print("\nInstruction Set:")
    for inst in instructions:
        print(" ", fmt(inst))

    show_dependencies(instructions)
    seq = sequential_execution(instructions)
    par = parallel_execution(instructions)

    speedup = seq / par
    print("\n" + "=" * 50)
    print("PERFORMANCE COMPARISON")
    print("=" * 50)
    print(f"Sequential Cycles : {seq}")
    print(f"ILP Cycles        : {par}")
    print(f"Speedup           : {speedup:.2f}x")
    print(f"ILP Efficiency    : {speedup / len(instructions) * 100:.2f}%")

    draw_dependency_graph(instructions)


if __name__ == "__main__":
    main()
