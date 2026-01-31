import { Typography, Card, Row, Col, Statistic, Progress } from "antd";
import { Area, Column } from "@ant-design/plots";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";
import { Text } from "@/components";

const { Title } = Typography;

export const CashflowReport = () => {
    // Cashflow Data (Daily balance + Bars for Income/Expense)
    const data = [
        { date: '01.01', income: 50000, expense: 20000, balance: 100000 },
        { date: '05.01', income: 150000, expense: 40000, balance: 210000 },
        { date: '10.01', income: 20000, expense: 80000, balance: 150000 },
        { date: '15.01', income: 300000, expense: 50000, balance: 400000 },
        { date: '20.01', income: 100000, expense: 120000, balance: 380000 },
        { date: '25.01', income: 50000, expense: 20000, balance: 410000 },
    ];

    const config = {
        data,
        xField: 'date',
        yField: 'balance',
        smooth: true,
        areaStyle: () => {
            return {
                fill: 'l(270) 0:#ffffff 0.5:#dbeafe 1:#1677ff',
            };
        },
        line: { color: '#1677ff' }
    };

    const barConfig = {
        data: [
            { type: 'Поступления', value: 3450000 },
            { type: 'Выплаты', value: 2150000 },
        ],
        xField: 'type',
        yField: 'value',
        seriesField: 'type',
        color: ({ type }: any) => {
            return type === 'Поступления' ? '#52c41a' : '#f5222d';
        },
        // label: {
        //     position: 'middle',
        //     style: { fill: '#FFFFFF', opacity: 0.6 },
        // },
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <Row gutter={[24, 24]}>
                <Col xs={24} md={12}>
                    <Card bordered={false} style={{ borderRadius: 16 }}>
                        <Statistic
                            title="Чистый денежный поток (Net Cashflow)"
                            value={1300000}
                            precision={0}
                            valueStyle={{ color: '#3f8600', fontWeight: 700 }}
                            prefix={<ArrowUpOutlined />}
                            suffix="₽"
                        />
                        <div style={{ marginTop: 12 }}>
                            <Text type="secondary">Эффективность сбора денег выше на 12% чем в прошлом месяце</Text>
                        </div>
                    </Card>
                </Col>
                <Col xs={24} md={12}>
                    <Card bordered={false} style={{ borderRadius: 16 }}>
                        <Title level={5}>Структура потоков</Title>
                        <div style={{ height: 100 }}>
                            <Column {...barConfig} autoFit />
                        </div>
                    </Card>
                </Col>
            </Row>

            <Card
                title="Движение денежных средств (ДДС)"
                bordered={false}
                style={{ borderRadius: 16 }}
            >
                <Area {...config} height={300} />
            </Card>
        </div>
    );
};
