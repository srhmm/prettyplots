import pandas as pd
import numpy as np
import sys


def comp_box_stats(in_file, sel_cols=None):
    """ Prepares boxplot statistics (whisker bottom, box bottom, median, box top, whisker top), saving to <in_file>_stats.csv."""
    if in_file.endswith(".tsv"):
        delim = "\t"
        out_file = in_file.replace(".tsv", "_stats.csv")
    elif in_file.endswith(".csv"):
        delim = ","
        out_file = in_file.replace(".csv", "_stats.csv")
    else:
        print("Unsupported file format. Please use a .csv or .tsv file.")
        sys.exit(1)
    df = pd.read_csv(in_file, delimiter=delim)

    sel_cols = list(df.columns) if sel_cols is None else sel_cols
    stats_list = []
    for i, col in enumerate(sel_cols):
        if col not in df.columns:
            print(f"Warning: {col} not found in the data.")
            continue

        data = df[col].dropna().to_numpy()
        if len(data) == 0: continue
        Q1 = np.percentile(data, 25)
        Q2 = np.median(data)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_whisker = np.min(data[data >= Q1 - 1.5 * IQR])
        upper_whisker = np.max(data[data <= Q3 + 1.5 * IQR])

        stats_list.append([lower_whisker, Q1, Q2, Q3, upper_whisker, col])

    stats_df = pd.DataFrame(stats_list, columns=["lw", "lq", "med", "uq", "uw", "name"])
    stats_df.to_csv(out_file, index=False)
    print(f"Statistics saved to {out_file}")

    return out_file


def gen_tikz_code(stats_filename):

    latex_code = f"""
\\pgfplotstableread[col sep = comma]{{{stats_filename}}}\\datatable
\\begin{{tikzpicture}}
\\begin{{axis}}[pretty boxplot, boxplot/draw direction=y]
\\pgfplotstablegetrowsof{{\\datatable}}
\\pgfmathtruncatemacro\\TotalRows{{\\pgfplotsretval-1}}
\\pgfplotsinvokeforeach{{0,...,\\TotalRows}}
{{
    \\addplot+[
    boxplot prepared from table={{
        table=\\datatable,
        row=#1,
        lower whisker=lw,
        upper whisker=uw,
        lower quartile=lq,
        upper quartile=uq,
        median=med
    }},
    boxplot prepared,
    ]
    coordinates {{}};

    %% comment out if column names should be legend entries: 
    %\\pgfplotstablegetelem{{#1}}{{name}}\\of\\datatable
    %\\addlegendentryexpanded{{\\pgfplotsretval}}
}}
\\end{{axis}}
\\end{{tikzpicture}}
"""
    print(f"\n%tikz code ({stats_filename}):\n")
    print(latex_code)
    with open(stats_filename.replace("_stats.csv", ".tex"), "w") as text_file:
        text_file.write(latex_code)

    return latex_code



def sample_data(output_filename="box.csv", num_columns=50, num_rows=500):
    np.random.seed(42)
    df = pd.DataFrame({
        f"Box{i+1}": np.random.normal(loc=np.random.randint(5, 15), scale=2, size=num_rows)
        for i in range(num_columns)
    })
    df.to_csv(output_filename, sep=",", index=False)
    print(f"Sample data saved to {output_filename}")


def test():
    file_name="box-large.csv"
    sample_data(file_name)

    stats_filename = comp_box_stats(file_name)
    gen_tikz_code(stats_filename)


if __name__ == "__main__":
    test()
    if len(sys.argv) < 2:
        print("Usage:\n\tpython boxplot_generator.py <file.csv or file.tsv> [<optional column names>]")
        sys.exit(1)

    in_name = sys.argv[1]
    sel_cols = sys.argv[2:] if len(sys.argv) > 2 else None
    stats_filename = comp_box_stats(in_name, sel_cols)
    gen_tikz_code(stats_filename)

