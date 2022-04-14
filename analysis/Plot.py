
import seaborn as sns
# Apply the default theme
sns.set_theme()

from matplotlib import pyplot as plt


class Plot:

    @staticmethod
    def plot2MatricesDF(data, col1, col2, col1name, col2name):
        g = sns.lineplot(data=data, x=col1, y=col2)
        plt.xlabel(col1name)
        plt.ylabel(col2name)
        plt.show()
    pass

    @staticmethod
    def plotMultipleEpisode(episode_dict, col1, col2, col1name, col2name):
        for key, val in episode_dict.items():
            g = sns.lineplot(data=val, x=col1, y=col2)
            plt.xlabel(col1name)
            plt.ylabel(col2name)
            plt.show()
        pass

    # @staticmethod
    # def plotDisPlot(data, col1, col1name):
    #     g = sns.displot(data=data, x=col1, bins=30)
    #     plt.xlabel(col1name)
    #     plt.ylabel('count')
    #     plt.axvline(x=data.col1.mean(), color='red')
    #     plt.show()