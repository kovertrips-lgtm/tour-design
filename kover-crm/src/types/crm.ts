export interface Tag {
    id: string;
    name: string;
    color: string;
}

export interface Task {
    id: string;
    text: string;
    due: string;
    completed: boolean;
}

export interface Note {
    id: string;
    text: string;
    author: string;
    date: string;
    type: 'note' | 'call' | 'email' | 'system';
}

export interface Contact {
    id: string;
    name: string;
    email?: string;
    phone?: string;
    position?: string;
    company?: string;
}

export interface Deal {
    id: string;
    title: string;
    price: number;
    currency: string;
    status: 'new' | 'contacted' | 'deposit' | 'paid';
    contact: Contact;
    tags: Tag[];
    tasks: Task[];
    notes: Note[];
    created_at: string;
}

export const MOCK_DEALS: Deal[] = [
    {
        id: '1023',
        title: 'Alps Tour - Family Smith',
        price: 2400,
        currency: 'EUR',
        status: 'new',
        contact: { id: 'c1', name: 'John Smith', phone: '+1 234 567 890', email: 'john@gmail.com' },
        tags: [{ id: 't1', name: 'VIP', color: '#8b5cf6' }, { id: 't2', name: 'Winter', color: '#3b82f6' }],
        tasks: [{ id: 'tsk1', text: 'Call to confirm dates', due: 'Today', completed: false }],
        notes: [
            { id: 'n1', text: 'Created deal from Website Widget', author: 'System', date: '2024-01-23 10:00', type: 'system' }
        ],
        created_at: '2024-01-23'
    },
    {
        id: '1024',
        title: 'Skiing Masterclass',
        price: 850,
        currency: 'EUR',
        status: 'contacted',
        contact: { id: 'c2', name: 'Maria Garcia', phone: '+34 999 888 777' },
        tags: [{ id: 't3', name: 'Solo', color: '#f59e0b' }],
        tasks: [],
        notes: [
            { id: 'n2', text: 'Client asked about equipment rental', author: 'Alex', date: '2024-01-22 14:30', type: 'call' }
        ],
        created_at: '2024-01-22'
    },
    {
        id: '1025',
        title: 'Hiking Group A (May)',
        price: 3200,
        currency: 'EUR',
        status: 'deposit',
        contact: { id: 'c3', name: 'Alex K.', company: 'Kover Travel' },
        tags: [{ id: 't4', name: 'Group', color: '#10b981' }],
        tasks: [{ id: 'tsk2', text: 'Send final invoice', due: 'Tomorrow', completed: false }],
        notes: [],
        created_at: '2024-01-20'
    },
];
