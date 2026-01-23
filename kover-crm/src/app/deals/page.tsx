'use client';

import React, { useState } from 'react';
import {
    DndContext,
    DragOverlay,
    closestCorners,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragStartEvent,
    DragOverEvent,
    DragEndEvent
} from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { MOCK_DEALS, Deal } from '@/types/crm';
import { Plus, Search, Filter } from 'lucide-react';
import DealPanel from '@/components/DealPanel';
import KanbanColumn from '@/components/KanbanColumn';
import KanbanCard from '@/components/KanbanCard';

const COLUMNS = [
    { id: 'new', title: 'New Request', color: '#3b82f6' },
    { id: 'contacted', title: 'Contacted', color: '#8b5cf6' },
    { id: 'deposit', title: 'Deposit Paid', color: '#f59e0b' },
    { id: 'paid', title: 'Fully Paid', color: '#10b981' },
];

export default function DealsPage() {
    const [deals, setDeals] = useState<Deal[]>(MOCK_DEALS);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);

    const sensors = useSensors(
        useSensor(PointerSensor, { activationConstraint: { distance: 5 } }), // Fix for click vs drag
        useSensor(KeyboardSensor)
    );

    // Find container logic (which column is it in?)
    const findContainer = (id: string) => {
        if (COLUMNS.find(c => c.id === id)) return id;
        const deal = deals.find(d => d.id === id);
        return deal?.status;
    };

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragOver = (event: DragOverEvent) => {
        const { active, over } = event;
        if (!over) return;

        // Just visual feedback, actual data update happens in DragEnd for this simple case
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        const activeDealId = active.id;
        const overId = over?.id; // Could be a column ID or a card ID

        if (!overId) {
            setActiveId(null);
            return;
        }

        // Determine target status
        let newStatus = '';
        const isOverColumn = COLUMNS.find(c => c.id === overId);

        if (isOverColumn) {
            newStatus = overId as string;
        } else {
            // Over another card, find that card's status
            const overDeal = deals.find(d => d.id === overId);
            if (overDeal) newStatus = overDeal.status;
        }

        if (newStatus) {
            setDeals((prev) => prev.map(deal =>
                deal.id === activeDealId
                    ? { ...deal, status: newStatus as any }
                    : deal
            ));
        }

        setActiveId(null);
    };

    return (
        <div style={{ height: 'calc(100vh - 80px)', display: 'flex', flexDirection: 'column' }}>

            {/* Header */}
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <h1 style={{ fontSize: '28px', fontWeight: 700 }}>Sales Pipeline</h1>
                    <div style={{ background: 'var(--bg-card)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '8px', width: '300px' }}>
                        <Search size={16} color="var(--text-muted)" />
                        <input placeholder="Search deals..." style={{ background: 'transparent', border: 'none', outline: 'none', color: 'white', fontSize: '14px', width: '100%' }} />
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', color: 'var(--text-muted)', cursor: 'pointer' }}>
                        <Filter size={20} />
                    </button>
                    <button style={{ background: 'var(--primary)', border: 'none', padding: '10px 20px', borderRadius: '8px', color: 'white', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                        <Plus size={18} /> New Deal
                    </button>
                </div>
            </header>

            {/* Kanban Board */}
            <DndContext
                sensors={sensors}
                collisionDetection={closestCorners}
                onDragStart={handleDragStart}
                onDragOver={handleDragOver}
                onDragEnd={handleDragEnd}
            >
                <div style={{
                    display: 'flex',
                    gap: '16px',
                    overflowX: 'auto',
                    paddingBottom: '20px',
                    flex: 1
                }}>
                    {COLUMNS.map(col => (
                        <KanbanColumn
                            key={col.id}
                            id={col.id}
                            title={col.title}
                            color={col.color}
                            deals={deals.filter(d => d.status === col.id)}
                            onCardClick={(deal) => setSelectedDeal(deal)}
                        />
                    ))}
                </div>

                {/* Drag Overlay for smooth visuals */}
                <DragOverlay>
                    {activeId ? (
                        <KanbanCard
                            deal={deals.find(d => d.id === activeId)!}
                            overlay
                        />
                    ) : null}
                </DragOverlay>
            </DndContext>

            {/* Modal / Slide-over */}
            {selectedDeal && (
                <DealPanel
                    deal={selectedDeal}
                    onClose={() => setSelectedDeal(null)}
                />
            )}
        </div>
    );
}
