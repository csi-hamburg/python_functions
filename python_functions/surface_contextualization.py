# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_surface_contextualization.ipynb.

# %% auto 0
__all__ = ['plot_surface', 'surface_to_schaefer', 'perform_spins', 'plot_null_distributions']

# %% ../01_surface_contextualization.ipynb 3
def plot_surface(
    surface:str, # Surface to plot on (default: fslr32k). Valid choices are “fslr32k”, “fsaverage”, “fsaverage3”, “fsaverage4”, “fsaverage5”, “fsaverage6”, “civet41k”, “civet164k”.
    values, # numpy array of values to plot (has to match the number of vertices in the surface)
    label_text:str, # text to label the plot
    color_range:tuple=None, # color range to use
    cmap="Blues" # color map to use
    )->object: # Plot 
    "Plots metric values on surface"
    
    # Plot cortical surfaces with values as the data, label_text as
    # the labels, and color_range as the limits of the color bar.
    from brainstat.datasets import fetch_mask, fetch_template_surface

    # Load behavioral markers
    pial_left, pial_right = fetch_template_surface(surface, join=False)
    pial_combined = fetch_template_surface(surface, join=True)
    mask = fetch_mask(surface)

    
    from brainspace.plotting import plot_hemispheres
    import numpy as np

    if not color_range:
        color_range = (np.nanmin(values), np.nanmax(values))

    return plot_hemispheres(
        pial_left,
        pial_right,
        values,
        color_bar=True,
        color_range=color_range,
        label_text=[label_text],
        cmap=cmap,
        embed_nb=True,
        size=(1400, 200),
        zoom=1.45,
        nan_color=(0.5, 0.5, 0.5, 1),
        cb__labelTextProperty={"fontSize": 12},
        interactive=False,
    )

# %% ../01_surface_contextualization.ipynb 4
import numpy as np

def surface_to_schaefer(
    array:np.array, # array with surface values, has to match vertex count
    surface:str, # surface to parcellate; valid choices: ('fslr32k')
    atlas_resolution:str, # atlas resolution; valid choices: ('400x7')
)->np.array: # Schaefer-parcellated metric
    "Harnesses neuromaps to schaefer-parcellate metrics on surface"

    from neuromaps.parcellate import Parcellater
    from netneurotools import datasets as nntdata
    from neuromaps.images import dlabel_to_gifti

    parc_space_dict = {
        'fslr32k':'fsLR'
    }

    atlas_dict = {
        "400x7":'400Parcels7Networks',
        "200x7":'200Parcels7Networks',
        "100x7":'100Parcels7Networks',
        "400x17":'400Parcels17Networks',
        "200x17":'200Parcels17Networks',
        "100x17":'100Parcels17Networks',
    }

    schaefer = nntdata.fetch_schaefer2018(surface)[atlas_dict[atlas_resolution]]
    parc = Parcellater(dlabel_to_gifti(schaefer), parc_space_dict[surface])

    return parc.fit_transform(array.squeeze(), parc_space_dict[surface])

# %% ../01_surface_contextualization.ipynb 5
import numpy as np

def perform_spins(
    array:np.array, # array with Schaefer-parcellated metric
    reference_array:np.array, # reference array with Schaefer-parcellated metric
    atlas_resolution:str, # atlas resolution; valid choices: ("100","200",'400')
    ):
    "Perform spin permutations on Schaefer-parcellated data; returns spearman correlation, p-value and permuted correlations"

    import numpy as np
    from scipy.stats import spearmanr
    from enigmatoolbox.permutation_testing import spin_test

    # Perform spatial correlations
    fin_idx = np.isfinite(array) & np.isfinite(reference_array)
    r = spearmanr(array[fin_idx], reference_array[fin_idx])[0]
    p, d = spin_test(array, reference_array, surface_name='fsa5', parcellation_name=f'schaefer_{atlas_resolution}',
                                type='spearman', n_rot=1000, null_dist=True)


    return r, p, d

# %% ../01_surface_contextualization.ipynb 6
def plot_null_distributions(
    r:float, # correlation between metric and reference
    p:float, # p-value
    d:np.array, # array with permuted correlations
    xlabel:str, # x axis label
    color:str, # color to use for the plot (hex code, rgb, or named color)
    ):
    "Plots null distribution of correlations"
    
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(1, 1, figsize=(6, 3))


    # Plot null distributions

    axs.hist(d, bins=50, density=True, color=color, edgecolor='white', lw=0.5)

    axs.axvline(r, lw=1.5, ls='--', color='k', dashes=(2, 3),

                label=f'$r_{{sp}}$={r:.2f}' + f'\n$p_{{spin}}$={p:.3f}')

    axs.set_xlabel(f'Null correlations \n ({xlabel})')

    axs.set_ylabel('Density')

    axs.spines['top'].set_visible(False)

    axs.spines['right'].set_visible(False)

    axs.legend(loc=1, frameon=False)

    fig.tight_layout()

    plt.show()

    return fig

