# AUTOGENERATED! DO NOT EDIT! File to edit: ../02_plotting.ipynb.

# %% auto 0
__all__ = ['plot_scatter']

# %% ../02_plotting.ipynb 3
def plot_scatter(
    array1, # array with values to plot on the x-axis
    measure_name1:str, # name of the measure to plot on the x-axis
    array2, # array with values to plot on the y-axis
    measure_name2:str, # name of the measure to plot on the y-axis
    annotation_dict:dict, # dictionary with annotations to plot 
    cmap:str=None, # color map to use
    loc_annot:str="upper right", # location of the annotation
    frameon_annot:bool=False, # whether to show the frame of the annotation
    pad_annot:float=None, # padding of the annotation
    tick_formatting:tuple=None, # formatting strings for xaxis and yaxis; e.g. ("%.2f","%.2f") 
    ):

    import seaborn as sns
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import AnchoredText
    from matplotlib.ticker import FormatStrFormatter
    
    fig, axs = plt.subplots(1, 1, figsize=(6, 3))

    axs.scatter(array1, array2, c=array1,
        
        cmap=cmap, edgecolors="black", linewidth=0.3)

    fin_idx = np.isfinite(array1) & np.isfinite(array2)
    m, b = np.polyfit(array1[fin_idx], array2[fin_idx], 1)

    axs.plot(array1, m * array1 + b, color="lightgray")

    annotation_list = []
    for k,v in annotation_dict.items():
        if type(v) is str: annotation_list.append(f'{k}={v}')
        else: annotation_list.append(f'{k}={v:.3f}')
    annotation_string = "   ".join(annotation_list)

    
    #annotation_string = f'$r_{{sp}}$={r:.2f} \n{pstring}={p:.3f}'
    at = AnchoredText(annotation_string, prop=dict(size=11), frameon=frameon_annot, borderpad=pad_annot, loc=loc_annot)
    axs.add_artist(at)

    axs.set_xlabel(f'{measure_name1}')

    axs.set_ylabel(f'{measure_name2}')

    axs.spines['top'].set_visible(False)

    axs.spines['right'].set_visible(False)

    axs.legend(loc=1, frameon=False, markerscale=0)

    if tick_formatting:

        axs.xaxis.set_major_formatter(FormatStrFormatter(tick_formatting[0]))

        axs.yaxis.set_major_formatter(FormatStrFormatter(tick_formatting[1]))

    fig.tight_layout()

    plt.show()

    return fig
