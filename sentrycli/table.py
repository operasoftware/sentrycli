from prettytable import PrettyTable


class Table(PrettyTable):

    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.align = 'l'
        self.align['count'] = 'r'
        self.align['%'] = 'r'
        self.float_format['%'] = '.1'

    def by_count(self):
        """
        Return table string sorted by 'count' key.
        :rtype: str
        """
        return self.get_string(sortby='count', reversesort=True)

    def add_rows(self, total, rows):
        """
        Add rows with values to the table along with count and percent columns.
        :param total: percentage will be calculated to this with this value
        :type: float
        :type rows: collections.Counter
        """
        for group_by, count in rows:
            self.add_row(list(group_by) + [count, count * 100.0 / total])
