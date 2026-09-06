import React from 'react'

export interface Filters {
  keyword: string
  city: string
  eligible_level: string
  department_category: string
  work_modality: string
  internship_type: string
  is_paid: boolean | null
  requires_mandatory_letter: boolean | null
}

interface FilterPanelProps {
  filters: Filters
  onChange: (filters: Filters) => void
}

const CITIES = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Kocaeli']
const LEVELS = [
  { id: '1_SINIF', label: '1. Sınıf' },
  { id: '2_SINIF', label: '2. Sınıf' },
  { id: '3_SINIF', label: '3. Sınıf' },
  { id: '4_SINIF', label: '4. Sınıf' },
  { id: 'YENI_MEZUN', label: 'Yeni Mezun' },
]
const DEPARTMENTS = [
  { id: 'MUHENDISLIK', label: 'Mühendislik' },
  { id: 'IIBF_ISLETME', label: 'İİBF / İşletme' },
  { id: 'FEN_BILIMLERI', label: 'Fen Bilimleri' },
  { id: 'TASARIM_MEDYA', label: 'Tasarım / Medya' },
]
const MODALITIES = [
  { id: 'OFISTE', label: 'Ofiste' },
  { id: 'UZAKTAN', label: 'Uzaktan' },
  { id: 'HIBRIT', label: 'Hibrit' },
]
const TYPES = [
  { id: 'ZORUNLU', label: 'Zorunlu' },
  { id: 'GONULLU', label: 'Gönüllü' },
  { id: 'UZUN_DONEM', label: 'Uzun Dönem' },
  { id: 'YAZ_STAJI', label: 'Yaz Stajı' },
]

export function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const updateFilter = (key: keyof Filters, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  const clearFilters = () => {
    onChange({
      keyword: filters.keyword, // keep search keyword
      city: '',
      eligible_level: '',
      department_category: '',
      work_modality: '',
      internship_type: '',
      is_paid: null,
      requires_mandatory_letter: null,
    })
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-6">
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Şehir</h3>
        <select
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm py-2 px-3 border"
          value={filters.city}
          onChange={(e) => updateFilter('city', e.target.value)}
        >
          <option value="">Tümü</option>
          {CITIES.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>
      </div>

      <div className="border-t border-gray-100 pt-5">
        <h3 className="font-semibold text-gray-900 mb-3">Öğrenci Seviyesi</h3>
        <div className="space-y-2">
          {LEVELS.map(level => (
            <label key={level.id} className="flex items-center">
              <input
                type="radio"
                name="level"
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                checked={filters.eligible_level === level.id}
                onChange={() => updateFilter('eligible_level', level.id)}
              />
              <span className="ml-2 text-sm text-gray-600">{level.label}</span>
            </label>
          ))}
          <label className="flex items-center">
              <input
                type="radio"
                name="level"
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                checked={filters.eligible_level === ''}
                onChange={() => updateFilter('eligible_level', '')}
              />
              <span className="ml-2 text-sm text-gray-600">Tümü</span>
            </label>
        </div>
      </div>

      <div className="border-t border-gray-100 pt-5">
        <h3 className="font-semibold text-gray-900 mb-3">Bölüm Kategorisi</h3>
        <div className="flex flex-wrap gap-2">
          {DEPARTMENTS.map(dept => (
            <button
              key={dept.id}
              onClick={() => updateFilter('department_category', filters.department_category === dept.id ? '' : dept.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                filters.department_category === dept.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {dept.label}
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-gray-100 pt-5">
        <h3 className="font-semibold text-gray-900 mb-3">Çalışma Modeli</h3>
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => updateFilter('work_modality', '')}
            className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${
              filters.work_modality === '' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Tümü
          </button>
          {MODALITIES.map(mod => (
            <button
              key={mod.id}
              onClick={() => updateFilter('work_modality', mod.id)}
              className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${
                filters.work_modality === mod.id ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              {mod.label}
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-gray-100 pt-5">
        <h3 className="font-semibold text-gray-900 mb-3">Staj Türü</h3>
        <div className="flex flex-wrap gap-2">
          {TYPES.map(type => (
            <button
              key={type.id}
              onClick={() => updateFilter('internship_type', filters.internship_type === type.id ? '' : type.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                filters.internship_type === type.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      <div className="border-t border-gray-100 pt-5 space-y-4">
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm font-semibold text-gray-900">Ücretli Staj</span>
          <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
            <input 
              type="checkbox" 
              name="toggle" 
              className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer border-gray-300 transition-transform duration-200 ease-in-out checked:translate-x-5 checked:border-primary-600"
              checked={filters.is_paid === true}
              onChange={(e) => updateFilter('is_paid', e.target.checked ? true : null)}
            />
            <label className="toggle-label block overflow-hidden h-5 rounded-full bg-gray-300 cursor-pointer"></label>
          </div>
        </label>
        
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm font-semibold text-gray-900">Zorunlu Staj Belgesi İster</span>
          <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
            <input 
              type="checkbox" 
              name="toggle" 
              className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer border-gray-300 transition-transform duration-200 ease-in-out checked:translate-x-5 checked:border-primary-600"
              checked={filters.requires_mandatory_letter === true}
              onChange={(e) => updateFilter('requires_mandatory_letter', e.target.checked ? true : null)}
            />
            <label className="toggle-label block overflow-hidden h-5 rounded-full bg-gray-300 cursor-pointer"></label>
          </div>
        </label>
      </div>

      <div className="border-t border-gray-100 pt-5">
        <button
          onClick={clearFilters}
          className="w-full py-2 text-sm font-medium text-gray-600 hover:text-gray-900 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
        >
          Filtreleri Temizle
        </button>
      </div>
      
      {/* Basic toggle CSS since native checkboxes don't style like switches easily without headless ui */}
      <style>{`
        .toggle-checkbox:checked {
          right: 0;
          border-color: #2563eb;
        }
        .toggle-checkbox:checked + .toggle-label {
          background-color: #3b82f6;
        }
        .toggle-checkbox {
          right: 20px;
          z-index: 1;
        }
      `}</style>
    </div>
  )
}
