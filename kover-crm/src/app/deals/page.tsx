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
    DragEndEvent
} from '@dnd-kit/core';
import { SortableContext } from '@dnd-kit/sortable';
import { Deal, MOCK_DEALS, PIPELINE_COLUMNS } from '@/types/crm';
import AmoKanbanCard from '@/components/AmoKanbanCard';
import AmoDealPanel from '@/components/AmoDealPanel';
import { Search, Plus, ListFilter, X } from 'lucide-react';

// Minimal Column Component (re-defined to be self-contained)
function Column({ id, title, color, deals, onCardClick }: any) {
    // SortableContext is needed for DndKit to know items exist here
    const total = deals.reduce((acc: number, d: Deal) => acc + d.price, 0);

    return (
        <div style={{
            minWidth: '280px',
            maxWidth: '280px',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            background: '#f0f0f0',
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

            {/* Droppable Area */}
            <SortableContext items={deals.map((d: Deal) => d.id)}>
                <div style={{ flex: 1, padding: '8px', overflowY: 'auto', background: '#eef2f5' }}>
                    {deals.map((deal: Deal) => (
                        <AmoKanbanCard
                            key={deal.id}
                            deal={deal}
                            onClick={() => onCardClick(deal)}
                        />
                    ))}
                    {deals.length === 0 && (
                        <div style={{ textAlign: 'center', padding: '20px', fontSize: '12px', color: '#aaa', border: '1px dashed #ccc', borderRadius: '4px' }}>
                            No deals
                        </div>
                    )}
                </div>
            </SortableContext>
        </div>
    );
}

export default function DealsPage() {
    const [deals, setDeals] = useState<Deal[]>(MOCK_DEALS);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);

    // New Deal Form State
    const [newDealTitle, setNewDealTitle] = useState('');
    const [newDealBudget, setNewDealBudget] = useState('');

    const sensors = useSensors(
        useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
    );

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        if (!over) {
            setActiveId(null);
            return;
        }

        const activeDealId = active.id as string;
        const overId = over.id as string;

        // Resolve Status
        let newStatus = '';
        // If dropped on column
        if (PIPELINE_COLUMNS.find(c => c.id === overId)) {
            newStatus = overId;
        } else {
            // If dropped on card
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

    const handleAddDeal = () => {
        if (!newDealTitle) return;
        const newDeal: Deal = {
            id: Math.floor(Math.random() * 100000).toString(),
            title: newDealTitle,
            price: Number(newDealBudget) || 0,
            currency: 'EUR',
            status_column_id: 'new',
            contact_name: 'Unknown',
            responsible: 'You',
            source: 'Manual',
            created_at: Date.now(),
            tags: [],
            fields: [],
            history: [{
                id: '1', type: 'system', author: 'System', text: 'Deal created manually', created_at: Date.now()
            }]
        };
        setDeals([newDeal, ...deals]);
        setShowAddModal(false);
        setNewDealTitle('');
        setNewDealBudget('');
    };

    // Filter deals
    const filteredDeals = deals.filter(d =>
        d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.contact_name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>

            {/* Top Bar */}
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
                        <input
                            placeholder="Search deals..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            style={{ border: 'none', background: 'transparent', width: '100%', fontSize: '13px', outline: 'none' }}
                        />
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '12px' }}>
                    <button style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600, color: '#313942', background: 'white', border: '1px solid #cfd8dc', padding: '6px 12px', borderRadius: '3px', cursor: 'not-allowed', opacity: 0.6 }}>
                        <ListFilter size={14} /> Pipeline: Main
                    </button>
                    <button
                        onClick={() => setShowAddModal(true)}
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'white', background: '#4c8bf5', border: 'none', padding: '6px 16px', borderRadius: '3px', cursor: 'pointer', textTransform: 'uppercase' }}
                    >
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
                    onDragEnd={handleDragEnd}
                >
                    {PIPELINE_COLUMNS.map(col => (
                        <Column
                            key={col.id}
                            id={col.id}
                            title={col.title}
                            color={col.color}
                            deals={filteredDeals.filter(d => d.status_column_id === col.id)}
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

            {/* New Deal Modal */}
            {showAddModal && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ background: 'white', padding: '24px', borderRadius: '4px', width: '400px', boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700 }}>Quick Add Deal</h3>
                            <X size={20} style={{ cursor: 'pointer', color: '#999' }} onClick={() => setShowAddModal(false)} />
                        </div>
                        <input
                            placeholder="Deal Title (e.g. Tour for Anna)"
                            autoFocus
                            value={newDealTitle}
                            onChange={e => setNewDealTitle(e.target.value)}
                            style={{ width: '100%', padding: '10px', marginBottom: '12px', border: '1px solid #ddd', borderRadius: '3px' }}
                        />
                        <input
                            placeholder="Budget (EUR)"
                            type="number"
                            value={newDealBudget}
                            onChange={e => setNewDealBudget(e.target.value)}
                            style={{ width: '100%', padding: '10px', marginBottom: '20px', border: '1px solid #ddd', borderRadius: '3px' }}
                        />
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                            <button onClick={() => setShowAddModal(false)} style={{ padding: '8px 16px', border: '1px solid #ddd', background: 'white', borderRadius: '3px', cursor: 'pointer' }}>Cancel</button>
                            <button onClick={handleAddDeal} style={{ padding: '8px 16px', border: 'none', background: '#4c8bf5', color: 'white', borderRadius: '3px', cursor: 'pointer', fontWeight: 600 }}>Create</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Slide Over */}
            {selectedDeal && (
                <AmoDealPanel
                    deal={selectedDeal}
                    onClose={() => setSelectedDeal(null)}
                    // Pass update handler to save notes/changes
                    onUpdate={(updated) => {
                        setDeals(prev => prev.map(d => d.id === updated.id ? updated : d));
                    }}
                />
            )}
        </div>
    );
}
