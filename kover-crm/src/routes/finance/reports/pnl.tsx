import { Typography, Table, Card, Tag } from "antd";
import { Text } from "@/components";

const { Title } = Typography;

export const PnLReport = () => {
    // Mock P&L Structure
    const data = [
        {
            key: 'revenue',
            category: 'Выручка (Поступления)',
            jan: 1250000,
            feb: 1540000,
            isGroup: true,
            children: [
                { key: 'tours', category: 'Продажа туров', jan: 1100000, feb: 1400000 },
                { key: 'upsell', category: 'Доп. услуги', jan: 150000, feb: 140000 },
            ]
        },
        {
            key: 'cos',
            category: 'Себестоимость',
            jan: -450000,
            feb: -620000,
            isGroup: true,
            children: [
                { key: 'hotels', category: 'Отели', jan: -250000, feb: -380000 },
                { key: 'transport', category: 'Транспорт', jan: -200000, feb: -240000 },
            ]
        },
        {
            key: 'gross_profit',
            category: 'Валовая прибыль',
            jan: 800000,
            feb: 920000,
            isTotal: true,
        },
        {
            key: 'opex',
            category: 'Операционные расходы',
            jan: -390000,
            feb: -410000,
            isGroup: true,
            children: [
                { key: 'salary', category: 'ФОТ', jan: -250000, feb: -250000 },
                { key: 'marketing', category: 'Маркетинг', jan: -100000, feb: -120000 },
                { key: 'office', category: 'Офис', jan: -40000, feb: -40000 },
            ]
        },
        {
            key: 'net_profit',
            category: 'Чистая прибыль',
            jan: 410000,
            feb: 510000,
            isTotal: true,
            isNet: true,
        },
    ];

    const columns = [
        {
            title: 'Статья',
            dataIndex: 'category',
            key: 'category',
            render: (text: string, record: any) => {
                if (record.isTotal) return <span style={{ fontWeight: 700, fontSize: 15 }}>{text}</span>;
                if (record.isGroup) return <span style={{ fontWeight: 600 }}>{text}</span>;
                return <span style={{ paddingLeft: 24, color: '#595959' }}>{text}</span>;
            }
        },
        {
            title: 'Янв 2026',
            dataIndex: 'jan',
            key: 'jan',
            align: 'right' as const,
            render: (val: number, record: any) => (
                <Text
                    strong={record.isTotal}
                    style={{
                        color: val < 0 ? '#f5222d' : record.isNet ? '#52c41a' : 'inherit',
                        fontSize: record.isNet ? 16 : 14
                    }}
                >
                    {val.toLocaleString()} ₽
                </Text>
            )
        },
        {
            title: 'Фев 2026',
            dataIndex: 'feb',
            key: 'feb',
            align: 'right' as const,
            render: (val: number, record: any) => (
                <Text
                    strong={record.isTotal}
                    style={{
                        color: val < 0 ? '#f5222d' : record.isNet ? '#52c41a' : 'inherit',
                        fontSize: record.isNet ? 16 : 14
                    }}
                >
                    {val.toLocaleString()} ₽
                </Text>
            )
        },
    ];

    return (
        <Card
            bordered={false}
            style={{ borderRadius: 16, boxShadow: "0 4px 20px rgba(0,0,0,0.03)" }}
            bodyStyle={{ padding: 0 }}
        >
            <div style={{ padding: "20px 24px", borderBottom: '1px solid #f0f0f0' }}>
                <Title level={4} style={{ margin: 0 }}>Отчет о прибылях и убытках (P&L)</Title>
            </div>
            <Table
                dataSource={data}
                columns={columns}
                pagination={false}
                expandable={{
                    defaultExpandAllRows: true,
                    expandIcon: () => null // Hide expand icon to make it look like a rigid report for now, or use proper tree structure
                }}
                rowKey="key"
                size="middle"
            />
        </Card>
    );
};
