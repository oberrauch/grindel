# ------------------------
# List of selected colors 
# ------------------------
# This helps to have a consistent color scheme
# throughout a project. If colors are added, the
# 'colors' name list must be updated as well.
# 
# With 'view()' all colors and their names are displayed.

# import section
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# specify colors with name and value
precip = '#1e3799'  # dark blue
precip2 = '#003049'  # dark blue
slf = '#8DDBE0'  # light blue
slf2 = '#427AA1'  # light blue
temp = '#D17A22'  # red
temp2 = '#770909'  # red
histalp = '#736F4E'  # green
histalp2 = '#3B3923'  # green
glacier = '#FCBF49'  # orange
glacier2 = '#F77F00'  # orange

negative = '#d91e18'  # red
negative2 = '#4C061D'  # red
positive = '#A5BE00'  # green
positive2 = '#679436'  # green


# list with all color names
colors = ['precip', 'precip2', 'slf', 'slf2', 'temp', 'temp2',
            'histalp', 'histalp2', 'glacier', 'glacier2',
            'negative', 'negative2', 'positive', 'positive2']


def view(hex=False):
    """ Plots all colors with their names. Code recycled from 
    https://matplotlib.org/examples/color/colormaps_reference.html
    """

    # create figure and axes
    fig, axes = plt.subplots(nrows=len(colors))
    fig.subplots_adjust(top=0.95, bottom=0.01, left=0.5, right=0.99)

    # add title
    title = 'Grindelwald project colors'
    axes[0].set_title(title, fontsize=14)

    # iterate over all colors
    for ax, name in zip(axes, colors):
        # create 'colormap' with one color
        color = eval(name)
        cmap = mcolors.LinearSegmentedColormap.from_list(
            name, [color, color])
        # plot single color
        ax.imshow([[1]], aspect='auto', cmap=cmap)
        # specify text position
        pos = list(ax.get_position().bounds)
        x_text = pos[0] - 0.01
        y_text = pos[1] + pos[3]/2.
        # add color name
        fig.text(x_text, y_text, name, va='center', ha='right', fontsize=12)
        
        # add color in hexadecimal notation
        if hex:
            # specify text position
            pos = list(ax.get_position().bounds)
            x_text = pos[0] + pos[2] + 0.01
            y_text = pos[1] + pos[3]/2.
            # add color name
            fig.text(x_text, y_text, eval(name), va='center', ha='left', fontsize=12)


    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axes:
        ax.set_axis_off()

    plt.show()

