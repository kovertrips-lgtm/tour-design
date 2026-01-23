'use client';

import React, { useState } from 'react';
import {
    DndContext,
    DragOverlay,
    closestCorners,
    useSensor,
    useSensors,
    PointerSensor,
    DragStartEvent,
    DragOverEvent,
    DragEndEvent
} from '@dnd-kit/core';
import { SortableContext, useSortable } from '@dnd-kit/sortable';
import { Deal, MOCK_DEALS, PIPELINE_COLUMNS } from '@/types/crm';
import AmoKanbanCard from '@/components/AmoKanbanCard';
import AmoDealPanel from '@/components/AmoDealPanel';
import { Search, Plus, ListFilter, Settings } from 'lucide-react';

// Minimal Column Component
function Column({ id, title, color, deals, onCardClick }: any) {
    const { setNodeRef } = useSortable({ id, disabled: true }); // Disabled sort for column itself

    const total = deals.reduce((acc: number, d: Deal) => acc + d.price, 0);

    return (
        <div ref={setNodeRef} style={{
            minWidth: '280px',
            maxWidth: '280px',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            background: '#f0f0f0', // Column gap color
            borderRight: '1px solid #e0e0e0'
        }}>
            {/* Header */}
            <div style={{ padding: '10px 12px', background: '#f5f5fa', borderBottom: '2px solid #ddd' }}>
                <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#555', marginBottom: '4px' }}>
                    {title}
                </div>
                <div style={{ fontSize: '11px', color: '#888' }}>
                    {deals.length} deals: <b style={{ color: '#333' }}>{total.toLocaleString()}</b>
                </div>
                <div style={{ height: '3px', width: '100%', background: color, marginTop: '8px' }}></div>
            </div>

            {/* Content */}
            <div style={{ flex: 1, padding: '8px', overflowY: 'auto', background: '#eef2f5' }}>
                <SortableContext items={deals.map((d: Deal) => d.id)}>
                    {deals.map((deal: Deal) => (
                        <AmoKanbanCard
                            key={deal.id}
                            deal={deal}
                            onClick={() => onCardClick(deal)}
                        />
                    ))}
                </SortableContext>
                {deals.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', color: '#aaa', border: '1px dashed #ccc', borderRadius: '4px' }}>
                        No deals
                    </div>
                )}
            </div>
        </div>
    );
}

export default function DealsPage() {
    const [deals, setDeals] = useState<Deal[]>(MOCK_DEALS);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);

    const sensors = useSensors(
        useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
    );

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragOver = (event: DragOverEvent) => {
        // Visual placeholder logic handled by SortableContext
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        if (!over) {
            setActiveId(null);
            return;
        }

        const activeDealId = active.id as string;
        const overId = over.id as string;

        // Find new status
        let newStatus = '';
        // Is over a column?
        if (PIPELINE_COLUMNS.find(c => c.id === overId)) {
            newStatus = overId;
        } else {
            // Is over a card?
            const overDeal = deals.find(d => d.id === overId);
            if (overDeal) newStatus = overDeal.status_column_id;
        }

        if (newStatus) {
            setDeals((prev) => prev.map(d =>
                d.id === activeDealId ? { ...d, status_column_id: newStatus } : d
            ));
        }
        setActiveId(null);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>

            {/* Top Bar (Amo Style) */}
            <div style={{
                height: '56px',
                background: 'white',
                borderBottom: '1px solid #dcdcdc',
                display: 'flex',
                alignItems: 'center',
                padding: '0 20px',
                justifyContent: 'space-between',
                flexShrink: 0
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#313942' }}>Deals</div>
                    <div style={{ display: 'flex', background: '#f0f2f5', borderRadius: '3px', padding: '6px 10px', alignItems: 'center', width: '250px' }}>
                        <Search size={14} color="#8c9fa6" style={{ marginRight: '8px' }} />
                        <input placeholder="Search and filter" style={{ border: 'none', background: 'transparent', width: '100%', fontSize: '13px', outline: 'none' }} />
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '12px' }}>
                    <button style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600, color: '#313942', background: 'white', border: '1px solid #cfd8dc', padding: '6px 12px', borderRadius: '3px', cursor: 'pointer' }}>
                        <ListFilter size={14} /> Pipeline: Main
                    </button>
                    <button style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'white', background: '#4c8bf5', border: 'none', padding: '6px 16px', borderRadius: '3px', cursor: 'pointer', textTransform: 'uppercase' }}>
                        <Plus size={14} /> New Deal
                    </button>
                </div>
            </div>

            {/* Board Area */}
            <div style={{ flex: 1, overflowX: 'auto', overflowY: 'hidden', display: 'flex', background: '#eef2f5' }}>
                <DndContext
                    sensors={sensors}
                    collisionDetection={closestCorners}
                    onDragStart={handleDragStart}
                    onDragOver={handleDragOver}
                    onDragEnd={handleDragEnd}
                >
                    {PIPELINE_COLUMNS.map(col => (
                        <Column
                            key={col.id}
                            id={col.id}
                            title={col.title}
                            color={col.color}
                            deals={deals.filter(d => d.status_column_id === col.id)}
                            onCardClick={(d: Deal) => setSelectedDeal(d)}
                        />
                    ))}

                    <DragOverlay>
                        {activeId ? (
                            <AmoKanbanCard deal={deals.find(d => d.id === activeId)!} onClick={() => { }} overlay />
                        ) : null}
                    </DragOverlay>

                </DndContext>
            </div>

      /* Slide Over */
            {selectedDeal && (
                <AmoDealPanel deal={selectedDeal} onClose={() => setSelectedDeal(null)} />
            )}
        </div>
    );
}
