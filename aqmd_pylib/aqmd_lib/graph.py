import os
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
import seaborn as sns

from sub_modules import  error_code as err

class graph_2d:
    _xid = 'xvar'

    def __init__(self, title=None, xAxisLabel='Independent', yAxisLabel='Dependent',
                 figWidth=15, figHeight=10, figDPI=100, faceColor='azure'):
        self._title = title
        self._xAxisLabel = xAxisLabel
        self._yAxisLabel = yAxisLabel
        self._figWidth = figWidth
        self._figHeight = figHeight
        self._figDPI = figDPI
        self._facecolor = faceColor

        self._plotFig, self._plotAx = None, None
        self._lineID = []
        self._scatterID = []
        self._lineData = []
        self._scatterData = []
        self._lineMelt = None
        self._scatterMelt = None

        self._tableFig, self._tableAx = None, None
        self._cellText = self._rowLabels = self._colLabels = self._contrastColor = None
        return

    def _prepData(self):
        if self._lineData is not None:
            self._linemelt = self._melter(self._lineData[0])
            if len(self._lineData) > 1:
                for i in range(1, len(self._lineData)):
                    self._lineMelt = pd.concat([self._lineMelt, self._melter(self._lineData[i])], axis=0)
        if self._scatterData is not None:
            self._scatterMelt = self._melter(self._scatterMelt[0])
            if len(self._scatterData) > 1:
                for i in range(1, len(self._lineData)):
                    self._scatterMelt = pd.concat([self._scatterMelt, self._melter(self._lineData[i])], axis=0)
        return

    def _melter(self, item):
        tmp = pd.concat([item[0], item[1]], axis=1)
        tmp = pd.melt(tmp, id_vars=list(item[1].columns)[0], value_vars=item[3], var_name=self._xid,
                      value_name=self._xAxisLabel)
        return tmp

    def _renderGraph(self):
        self._prepData()
        self._plotFig, self._plotAx = plt.subplots(dpi=self._figDPI,
                                                   figsize=(self._figWidth, self._figHeight),
                                                   facecolor=self._facecolor,
                                                   edgecolor="black")
        sns.lineplot(ax=self._plotAx,
                     data=self._lineMelt, x=str(self._xAxisLabel), y=str(self._yAxisLabel),
                     hue=self._xid, legend=False, palette='bright')
        sns.scatterplot(ax=self._plotAx,
                        data=self._scatterMelt, x=str(self._xAxisLabel), y=str(self._yAxisLabel),
                        hue=self._xid, legend='auto', palette='pastel', alpha=0.5)
        self._plotFig.suptitle(self._title)
        self._plotAx.grid(b=True, which='both', axis='both')
        return

    def _tableCheck(self):
        if ((self._cellText is None)
                or (self._rowLabels is None)
                or (self._colLabels is None)):
            return False
        else:
            return True

    def _renderTable(self):
        if self._tableCheck() is False:
            raise ValueError('Table elements must be set before table can be rendered')
        if self._figWidth < self._figHeight:
            tableSize = self._figWidth
        else:
            tableSize = self._figHeight
        self._tableFig, self._tableAx = plt.subplots(dpi=self._figDPI,
                                                     figsize=(tableSize, tableSize),
                                                     facecolor=self._facecolor,
                                                     edgecolor="black")
        self._tableFig.suptitle(self._title)
        self._tableAx.axis('off')
        rcolors = np.full(len(self._rowLabels), str(self._contrastColor))
        ccolors = np.full(len(self._colLabels), str(self._contrastColor))
        self._table = self._tableAx.add_table(cellText=self._cellText,
                                              rowLabels=self._rowLabels,
                                              colLabels=self._colLabels,
                                              rowColours=rcolors,
                                              colColours=ccolors,
                                              loc='center',
                                              bbox=[0.1, 0.2, 0.9, 0.8])

        return

    def _renderAll(self):
        self._renderGraph()
        self._renderTable()
        return

    def add_line(self, x, y):
        err.check_2d(x, y, 'graph_2d.add_line()')
        title = list(x.columns)[0]
        self._lineData.append((x, y, title))
        self._prepData()
        self._renderGraph()
        return

    def add_scatter(self, x, y):
        err.check_2d(x, y, 'graph_2d.add_scatter()')
        title = list(x.column)[0]
        self._scatterData.append((x, y, title))
        self._prepData()
        self._renderGraph()
        return

    def add_table(self, tableData, row_labels, col_labels,
                  contrast_color='palegreen'):
        self._cellText = tableData
        self._rowLabels = row_labels
        self._colLabels = col_labels
        self._contrastColor = contrast_color
        self._renderTable()
        return

    def finetune_table(self):
        return self._tableFig, self._tableAx, self._table

    def finetune_graph(self):
        return self._plotFig, self._plotAx

    def delete_table(self):
        self._table = None
        self._renderGraph()
        return

    def clear_lines(self):
        self._lineData = None
        self._lineMelt = None
        return

    def clear_scatters(self):
        self._scatterData = None
        self._scatterMelt = None
        return

    def delete_line(self, id: Union[str, int]):
        if type(id) is str:
            n = self._lineID.index(id)
        elif type(id) is int:
            n = id
        else:
            raise ValueError('id must be type str or int')
        del self._lineID[n]
        del self._lineData[n]
        return

    def delete_scatter(self, id: Union[str, int]):
        if type(id) is str:
            n = self._scatterID.index(id)
        elif type(id) is int:
            n = id
        else:
            raise ValueError('id must be type str or int')
        del self._scatterID[n]
        del self._scatterData[n]
        self._prepData()

        return

    def show(self):
        self._plotFig.show()
        if self._tableFig is not None:
            self._tableFig.show()

    def saveGraph(self, path, title, filetype='svg'):
        self._plotFig.savefig(fname=os.path.join(path, title + '.' + filetype),
                              dpi=self._figDPI, facecolor=self._facecolor,
                              edgecolor='black')
        return

    def saveTable(self, path, title, filetype='svg'):
        self._tableAx.savefig(fname=os.path.join(path,title+'.'+filetype),
                              dpi=self._figDPI, facecolor=self._facecolor,
                              edgecolor='black')
        return
