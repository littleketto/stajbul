import React from 'react'
import { Badge } from '@/components/Badge'
import { MapPin, Building2, ExternalLink } from 'lucide-react'
import { 
  cn, 
  formatRelativeDate, 
  getWorkModalityLabel, 
  getStudentLevelLabel,
  getConfidenceColor
} from '@/lib/utils'

interface ListingCardProps {
  listing: any // Using any for simplicity here, but should match Listing interface
}

export function ListingCard({ listing }: ListingCardProps) {
  const modalityLabel = getWorkModalityLabel(listing.work_modality)
  const modalityColor = listing.work_modality === 'UZAKTAN' 
    ? 'success' 
    : listing.work_modality === 'HIBRIT' 
      ? 'info' 
      : 'outline'

  const levels = listing.eligible_levels_json || []
  const depts = listing.eligible_departments_json || []

  return (
    <div 
      className="group relative flex flex-col justify-between bg-white rounded-xl border border-gray-200 p-5 shadow-sm transition-all hover:shadow-md cursor-pointer"
      onClick={() => window.open(listing.source_url, '_blank', 'noopener,noreferrer')}
    >
      <div>
        <div className="flex items-start justify-between">
          <div className="flex gap-4 items-start">
            <div className="h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 text-gray-500 font-semibold border border-gray-200">
              {listing.raw_company?.substring(0, 2).toUpperCase() || <Building2 className="w-6 h-6 text-gray-400" />}
            </div>
            <div>
              <h3 className="font-bold text-gray-900 line-clamp-2 text-lg group-hover:text-primary-600 transition-colors">
                {listing.raw_title}
              </h3>
              <p className="text-gray-500 text-sm mt-1">{listing.raw_company}</p>
            </div>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2 items-center text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span>{listing.city || listing.raw_location || 'Belirtilmemiş'}</span>
          </div>
          <span className="text-gray-300">•</span>
          <Badge variant={modalityColor as any}>{modalityLabel}</Badge>
        </div>

        <div className="mt-4 space-y-2">
          {levels.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {levels.map((level: string) => (
                <Badge key={level} variant="secondary" size="sm">
                  {getStudentLevelLabel(level)}
                </Badge>
              ))}
            </div>
          )}
          {depts.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {depts.slice(0, 3).map((dept: string) => (
                <span key={dept} className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                  {dept}
                </span>
              ))}
              {depts.length > 3 && (
                <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                  +{depts.length - 3} bölüm
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between border-t border-gray-100 pt-4">
        <div className="text-xs text-gray-500">
          {formatRelativeDate(listing.posted_date)}
        </div>
        <div className="flex items-center gap-2">
          {listing.extraction_confidence && (
            <div className={cn("px-2 py-1 rounded text-xs font-medium", getConfidenceColor(listing.extraction_confidence))}>
              {Math.round(listing.extraction_confidence * 100)}% Uyum
            </div>
          )}
          <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-primary-600" />
        </div>
      </div>
    </div>
  )
}
