import { useState } from 'react';
import { ChevronUp, ChevronDown, Search, Download } from 'lucide-react';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  formatter?: (value: any) => string;
}

interface CustomerTableProps {
  columns: Column[];
  data: Record<string, any>[];
  onRowClick?: (row: Record<string, any>) => void;
  searchableColumns?: string[];
  onExport?: () => void;
}

type SortDirection = 'asc' | 'desc' | null;

export const CustomerTable = ({
  columns,
  data,
  onRowClick,
  searchableColumns = [],
  onExport,
}: CustomerTableProps) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: SortDirection;
  }>({ key: '', direction: null });
  const [searchTerm, setSearchTerm] = useState('');

  // Filter data
  let filteredData = data;
  if (searchTerm && searchableColumns.length > 0) {
    filteredData = data.filter((row) =>
      searchableColumns.some((col) =>
        String(row[col]).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }

  // Sort data
  if (sortConfig.key && sortConfig.direction) {
    filteredData = [...filteredData].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }

  const handleSort = (key: string) => {
    let direction: SortDirection = 'asc';

    if (sortConfig.key === key) {
      if (sortConfig.direction === 'asc') {
        direction = 'desc';
      } else if (sortConfig.direction === 'desc') {
        direction = null;
      }
    }

    setSortConfig({
      key: direction ? key : '',
      direction,
    });
  };

  const getSortIcon = (key: string) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    );
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4 bg-[#111111] p-4 rounded-lg border border-[#1E293B]">
        {searchableColumns.length > 0 && (
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#64748B]" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#0A0A0A] border border-[#1E293B] rounded-lg text-[#FFFFFF] placeholder-[#64748B] focus:outline-none focus:border-[#06B6D4] transition-colors"
            />
          </div>
        )}

        {onExport && (
          <button
            onClick={onExport}
            className="px-4 py-2 flex items-center gap-2 bg-[#06B6D4]/20 text-[#06B6D4] border border-[#06B6D4]/50 rounded-lg hover:bg-[#06B6D4]/30 transition-colors font-medium text-sm"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-[#1E293B]">
        <table className="w-full">
          <thead>
            <tr className="bg-[#111111] border-b border-[#1E293B]">
              {columns.map((col) => (
                <th key={col.key} className="px-6 py-3 text-left">
                  {col.sortable ? (
                    <button
                      onClick={() => handleSort(col.key)}
                      className="flex items-center gap-2 font-semibold text-[#CBD5E1] hover:text-[#06B6D4] transition-colors"
                    >
                      {col.label}
                      {getSortIcon(col.key)}
                    </button>
                  ) : (
                    <div className="font-semibold text-[#CBD5E1]">
                      {col.label}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {filteredData.map((row, idx) => (
              <tr
                key={idx}
                onClick={() => onRowClick?.(row)}
                className={`border-b border-[#1E293B] hover:bg-[#111111] transition-colors ${
                  onRowClick ? 'cursor-pointer' : ''
                }`}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className="px-6 py-4 text-sm text-[#CBD5E1]"
                  >
                    {col.formatter
                      ? col.formatter(row[col.key])
                      : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {filteredData.length === 0 && (
          <div className="px-6 py-8 text-center text-[#64748B]">
            No customers found
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="text-xs text-[#64748B] text-right">
        Showing {filteredData.length} of {data.length} customers
      </div>
    </div>
  );
};
