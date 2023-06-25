import jetforkLogo from '../../logo_white_transporent.png';
import { Layout, Menu, Breadcrumb, theme } from 'antd';
import { Outlet, useNavigate } from 'react-router-dom';




export default function Header() {
    const {
        token: { colorBgContainer },
    } = theme.useToken();

    const navigate = useNavigate();

    const items = [
        {
            key: '1',
            label: 'Отправить на проверку',
            onClick: () => navigate('/'),
        },
        {
            key: '2',
            label: 'Проверить данные',
        },
    ]


    return (
        <Layout>
            <Layout.Header style={{ display: 'flex', alignItems: 'center' }}>
                <a href='/' rel="noreferrer" style={{ height: '100%' }}>
                    <img src={jetforkLogo} style={{ height: '100%', paddingRight: 50 }} />
                </a>
                <Menu theme="dark" mode="horizontal" items={items}
                    defaultSelectedKeys={['1']} />
            </Layout.Header>
            <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
                <Layout.Content style={{ padding: '0 50px', flex: 1, overflow: 'auto' }}>
                    <Breadcrumb style={{ margin: '16px 0' }}>
                        <Breadcrumb.Item>Главгосэкспертиза</Breadcrumb.Item>
                        <Breadcrumb.Item>Проверка данных</Breadcrumb.Item>
                    </Breadcrumb>
                    <div style={{ background: colorBgContainer, padding: 30, paddingInline: 100 }}>
                        <Outlet />
                    </div>
                </Layout.Content>
                <Layout.Footer style={{ textAlign: 'center' }}>JetFork</Layout.Footer>
            </div>
        </Layout>

    )
}
