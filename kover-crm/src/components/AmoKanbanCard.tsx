'use client';

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Deal } from '@/types/crm';
import { Tag as TagIcon, Phone, User } from 'lucide-react';

interface Props {
    deal: Deal;
    onClick: () => void;
    overlay?: boolean;
}

export default function AmoKanbanCard({ deal, onClick, overlay }: Props) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging
    } = useSortable({ id: deal.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.4 : 1,
        cursor: overlay ? 'grabbing' : 'grab',
        position: 'relative' as const,
        zIndex: isDragging ? 99 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...attributes}
            {...listeners}
            onClick={onClick}
            // AmoCRM simulation styles
            className="amo-card"
        >
            <style jsx>{`
        .amo-card {
          background: white;
          border-radius: 3px;
          border-bottom: 2px solid #e0e0e0; /* slight rigid feel */
          box-shadow: 0 1px 2px rgba(0,0,0,0.1);
          padding: 8px 10px;
          margin-bottom: 8px;
          font-size: 13px;
        }
        .amo-card:hover {
          box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }
        .tag {
          width: 24px;
          height: 6px;
          border-radius: 3px;
          margin-right: 4px;
          margin-bottom: 6px;
          display: inline-block;
        }
      `}</style>

            {/* Tags Line */}
            <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                {deal.tags.map(tag => (
                    <div key={tag.id} className="tag" style={{ background: tag.color }} title={tag.name} />
                ))}
            </div>

            {/* Title */}
            <div style={{ fontWeight: 600, color: '#313942', marginBottom: '8px', lineHeight: '1.3' }}>
                {deal.title}
            </div>

            {/* Price */}
            <div style={{ marginBottom: '8px', fontSize: '13px' }}>
                <span style={{ fontWeight: 700, color: '#313942' }}>{deal.price.toLocaleString()} {deal.currency}</span>
            </div>

            {/* Meta (Company/Contact) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8c9fa6', fontSize: '12px' }}>
                <User size={12} />
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%' }}>
                    {deal.contact_name}
                </span>
            </div>

            {/* Source Icon (Simulated) */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
                <div style={{ fontSize: '10px', background: '#f0f0f0', padding: '2px 4px', borderRadius: '3px', color: '#888' }}>
                    {deal.source}
                </div>
            </div>
        </div>
    );
}
