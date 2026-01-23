import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { MoreHorizontal, Calendar, DollarSign, User } from 'lucide-react';
import { Deal } from '@/types/crm';
import { clsx } from 'clsx';
import cardStyles from './Card.module.css'; // Reuse existing styles

interface KanbanCardProps {
    deal: Deal;
    onClick?: () => void;
    overlay?: boolean;
}

export default function KanbanCard({ deal, onClick, overlay }: KanbanCardProps) {
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
            className={cardStyles.card} // Use glass effect
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {deal.tags.map(tag => (
                        <span key={tag.id} style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            background: tag.color,
                            color: 'white',
                            fontWeight: 600
                        }}>
                            {tag.name}
                        </span>
                    ))}
                </div>
                <MoreHorizontal size={14} color="var(--text-muted)" />
            </div>

            <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px', lineHeight: '1.4' }}>{deal.title}</h4>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>
                <User size={12} /> {deal.contact.name}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    color: 'var(--primary)',
                    fontWeight: 600
                }}>
                    <DollarSign size={12} />
                    {deal.price}
                </div>

                {deal.tasks.length > 0 && (
                    <div style={{
                        fontSize: '11px',
                        background: 'var(--warning)',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '10px',
                        fontWeight: 700
                    }}>
                        !
                    </div>
                )}
            </div>
        </div>
    );
}
