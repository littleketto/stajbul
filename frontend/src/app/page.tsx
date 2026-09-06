'use client'

import { useState, useEffect, useCallback } from 'react'
import { FilterPanel, type Filters } from '@/components/FilterPanel'
import { ListingCard } from '@/components/ListingCard'
import { SearchBar } from '@/components/SearchBar'
import { Pagination } from '@/components/Pagination'
import { Loader2 } from 'lucide-react'

interface Listing {
  id: number
  raw_title: string
  raw_company: string
  raw_location: string
  source_url: string
  posted_date: string | null
  city: string | null
  work_modality: string | null
  internship_type: string | null
  is_paid: boolean | null
  requires_mandatory_letter: boolean | null
  summary_tr: string | null
  extraction_confidence: number | null
  eligible_levels_json: string[] | null
  department_categories_json: string[] | null
  eligible_departments_json: string[] | null
  required_skills_json: string[] | null
  application_deadline: string | null
}

interface ListingResponse {
  items: Listing[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

const DEFAULT_FILTERS: Filters = {
  keyword: '',
  city: '',
  eligible_level: '',
  department_category: '',
  work_modality: '',
  internship_type: '',
  is_paid: null,
  requires_mandatory_letter: null,
}

export default function HomePage() {
  const [listings, setListings] = useState<Listing[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS)

  const fetchListings = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('page', String(page))
      params.set('page_size', '12')
      
      if (filters.keyword) params.set('keyword', filters.keyword)
      if (filters.city) params.set('city', filters.city)
      if (filters.eligible_level) params.set('eligible_level', filters.eligible_level)
      if (filters.department_category) params.set('department_category', filters.department_category)
      if (filters.work_modality) params.set('work_modality', filters.work_modality)
      if (filters.internship_type) params.set('internship_type', filters.internship_type)
      if (filters.is_paid !== null) params.set('is_paid', String(filters.is_paid))
      if (filters.requires_mandatory_letter !== null) params.set('requires_mandatory_letter', String(filters.requires_mandatory_letter))

      const res = await fetch(`/api/v1/listings?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to fetch')
      const data: ListingResponse = await res.json()
      setListings(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      console.error('Fetch error:', err)
      setListings([])
    } finally {
      setLoading(false)
    }
  }, [page, filters])

  useEffect(() => {
    fetchListings()
  }, [fetchListings])

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters)
    setPage(1) // Reset to first page on filter change
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero/Search Section */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Staj Fırsatlarını Keşfet
        </h1>
        <p className="text-gray-500 mb-6">
          Türkiye'deki en güncel staj ilanları, yapay zeka ile analiz edildi
        </p>
        <SearchBar
          value={filters.keyword}
          onChange={(keyword) => handleFilterChange({ ...filters, keyword })}
        />
      </div>

      <div className="flex gap-8">
        {/* Left Sidebar: Filters */}
        <aside className="hidden lg:block w-72 flex-shrink-0">
          <FilterPanel filters={filters} onChange={handleFilterChange} />
        </aside>

        {/* Main Content */}
        <div className="flex-1">
          {/* Result count */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-500">
              {loading ? 'Yükleniyor...' : `${total} ilan bulundu`}
            </p>
          </div>

          {/* Listings Grid */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
              <span className="ml-3 text-gray-500">İlanlar yükleniyor...</span>
            </div>
          ) : listings.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-400 text-lg">Kriterlere uygun ilan bulunamadı</p>
              <p className="text-gray-400 text-sm mt-2">Filtreleri genişletmeyi deneyin</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {listings.map((listing) => (
                <ListingCard key={listing.id} listing={listing} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          )}
        </div>
      </div>
    </div>
  )
}
