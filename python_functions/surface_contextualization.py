# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_surface_contextualization.ipynb.

# %% auto 0
__all__ = ['plot_surface', 'surface_to_schaefer', 'perform_spins', 'plot_null_distributions', 'weighted_degree_centrality',
           'yeo_participation_coefficient', 'neighborhood_abnormality', 'connectivity_gradients']

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
def surface_to_schaefer(
    array, # array with surface values, has to match vertex count
    surface:str, # surface to parcellate; valid choices: ('fslr32k')
    atlas_resolution:str, # atlas resolution; valid choices: ('400x7')
):
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
def perform_spins(
    array, # array with Schaefer-parcellated metric
    reference_array, # reference array with Schaefer-parcellated metric
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
    d, # array with permuted correlations
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


# %% ../01_surface_contextualization.ipynb 7
def weighted_degree_centrality(
    mat, # adjacency matrix
    rank:bool=False, # whether to return the rank of the centrality measure
):
    "Compute weighted degree centrality measures from the connectivity data"
    import numpy as np
    
    dc = np.sum(mat, axis=0)

    if rank==True:
        return np.argsort(np.argsort(dc * -1))
    
    return dc 


# %% ../01_surface_contextualization.ipynb 8
def yeo_participation_coefficient(
    mat_df, # adjacency matrix as pandas dataframe with row and column index corresponding with Schaefer-parcellated region labels
    rank:bool=False, # whether to return the rank of participation coefficient
):
    "Computes participation coefficient of node with regard to Yeo networks"

    import numpy as np

    yeo_networks = ["Vis","SomMot","DorsAttn", "VentAttn", "Limbic", "Cont", "Default"]

    mat_degree = mat_df.sum(axis=0)
    rois = mat_df.columns

    PC_array = []

    for roi in rois:

        network_array = []
        for network in yeo_networks:
            
            roi_degree = mat_degree[roi]
            
            network_rois = [roi for roi in rois if network in roi]
            roi_to_network_df = mat_df.loc[roi,network_rois]

            roi_to_network_connectivity = roi_to_network_df.sum()

            network_array = np.append(network_array, (roi_to_network_connectivity / roi_degree) ** 2)

        PC_array = np.append(PC_array, (1 - network_array.sum()))

    if rank==True:
        return np.argsort(np.argsort(PC_array))

    return PC_array

# %% ../01_surface_contextualization.ipynb 9
def neighborhood_abnormality(
    adjacency, # adjacency matrix 
    metric, # nodewise metric matching node count of adjacency matrix 
    atlas_labels # atlas labels
    ):
    "Computes neighborhood abnormality index"
    import numpy as np

    nghbr_dict = {}

    for i in range(adjacency.shape[0]):

        mask_connected_nodes = adjacency[i] != 0
        n_connected_nodes = len(adjacency[i][mask_connected_nodes])

        weighted_measure_list = []

        for j in range(adjacency.shape[1]):

            if adjacency[i,j] != 0: weighted_measure_list.append(metric[j] * adjacency[i,j])

        weighted_measure_array = np.array(weighted_measure_list)
        sum_weighted_measure = sum(weighted_measure_array[~np.isnan(weighted_measure_array)])

        nghbr_dict[atlas_labels[i]] = sum_weighted_measure / n_connected_nodes
        
    return np.array(list(nghbr_dict.values()))

# %% ../01_surface_contextualization.ipynb 10
def connectivity_gradients(
    mat, # schaefer adjacency matrix
    gradient_nr, # gradient number to return
    atlas_resolution:str, # atlas resolution; valid choices: ("100","200",'400')
    ):

    import numpy as np
    from brainspace.datasets import  load_parcellation
    from brainspace.gradient import GradientMaps
    from brainspace.utils.parcellation import map_to_labels

    # Ask for 10 gradients (default)
    gm = GradientMaps(n_components=10, random_state=0)
    gm.fit(mat)

    # Load Schaefer parcellation mapping to conte69
    labeling = load_parcellation('schaefer', scale=atlas_resolution, join=True)
    mask = labeling != 0

    grad = [None] * 2

    for i in range(2):

        # map the gradient to the parcels
        grad[i] = map_to_labels(gm.gradients_[:, i], labeling, mask=mask, fill=np.nan)

    grad_schaefer = surface_to_schaefer(grad[gradient_nr], surface="fslr32k", atlas_resolution=f"{atlas_resolution}x7")

    return grad_schaefer, gm
