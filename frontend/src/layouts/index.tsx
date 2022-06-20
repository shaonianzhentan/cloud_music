import { createRef } from 'react'
import { IRouteComponentProps } from 'umi'
import { PageHeader, Layout, Menu, BackTop } from 'antd'
import type { MenuProps } from 'antd';
import styles from './index.less';
import { UserOutlined, BarChartOutlined, OrderedListOutlined, BarsOutlined, HomeOutlined } from '@ant-design/icons';
import PlayControl from '../components/layouts/PlayControl'

const { Header, Footer, Sider, Content } = Layout;

type MenuItem = Required<MenuProps>['items'][number];
function getItem(
    label: React.ReactNode,
    key: React.Key,
    icon?: React.ReactNode,
    children?: MenuItem[],
    type?: 'group',
): MenuItem {
    return {
        key,
        icon,
        children,
        label,
        type,
    } as MenuItem;
}

const items: MenuProps['items'] = [
    getItem('推荐', 'sub1', <BarChartOutlined />, [
        getItem('个性推荐', '/home/recommend'),
        getItem('歌单', '/home/playlist'),
        getItem('主播电台', '/home/radio'),
        getItem('排行榜', '/home/rank'),
        getItem('歌手', '/home/singer'),
        getItem('最新音乐', '/home/news')
    ]),

    getItem('我的音乐', 'sub2', <UserOutlined />, [
        getItem('本地音乐', '/my/local'),
        getItem('音乐云盘', '/my/cloud'),
        getItem('订阅电台', '/my/radio'),
        getItem('我的收藏', '/my/favorite')
    ]),

    getItem('创建的歌单', 'sub4', <OrderedListOutlined />, [
        getItem('Option 9', '9'),
    ]),

    getItem('收藏的歌单', 'sub5', <BarsOutlined />, [
        getItem('Option 10', '10'),
    ]),
];

export default function LayoutIndex({ children, location, route, history, match }: IRouteComponentProps) {

    const mainRef = createRef<HTMLElement>()

    const selectPath = ({ key }: any) => {
        history.push(key)
    };

    return (
        <>
            <Layout className={styles.layout}>
                <Header className={styles.header}>
                    <PageHeader
                        className={styles.pageHeader}
                        backIcon={<HomeOutlined style={{ fontSize: '20px', color: 'white' }} />}
                        onBack={() => null}
                        title="云音乐"
                    />
                </Header>
                <Layout>
                    <Sider className={styles.sider} theme="light">
                        <Menu
                            defaultSelectedKeys={['1']}
                            defaultOpenKeys={['sub1']}
                            mode="inline"
                            items={items}
                            onSelect={selectPath}
                        />
                    </Sider>
                    <Content ref={mainRef} className={styles.main}>  {children}

                        <BackTop target={() => mainRef.current as any} />
                    </Content>
                </Layout>
                <Footer className={styles.footer}>
                    <PlayControl />
                </Footer>
            </Layout>
        </>
    )
}