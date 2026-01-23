import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import KanbanCard from './KanbanCard';
import { Deal } from '@/types/crm';

interface KanbanColumnProps {
    id: string;
    title: string;
    color: string;
    deals: Deal[];
    onCardClick: (deal: Deal) => void;
}

export default function KanbanColumn({ id, title, color, deals, onCardClick }: KanbanColumnProps) {
    const { setNodeRef } = useSortable({ id });

    return (
        <div ref={setNodeRef} style={{
            minWidth: '320px',
            background: 'rgba(255,255,255,0.02)',
            borderRadius: '16px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            height: '100%'
        }}>
            {/* Column Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px',
                paddingBottom: '12px',
                borderBottom: `2px solid ${color}`
            }}>
                <span style={{ fontWeight: 600, fontSize: '14px', textTransform: 'uppercase' }}>{title}</span>
                <span style={{
                    background: 'rgba(255,255,255,0.1)',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px'
                }}>
                    {deals.length} ${deals.reduce((acc, d) => acc + d.price, 0).toLocaleString()}
                </span>
            </div>

            {/* Cards Container */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1, overflowY: 'auto' }}>
                {deals.map(deal => (
                    <KanbanCard
                        key={deal.id}
                        deal={deal}
                        onClick={() => onCardClick(deal)}
                    />
                ))}
                {deals.length === 0 && (
                    <div style={{
                        height: '100px',
                        border: '1px dashed var(--border)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--text-muted)',
                        fontSize: '13px'
                    }}>
                        No deals
                    </div>
                )}
            </div>
        </div>
    );
}
