import { IRouteComponentProps } from 'umi'
import React, { useEffect, useState } from 'react';
import styles from './playlist.less';
import type { ColumnsType } from 'antd/lib/table';
import { Card, Space, Button, Table, message, BackTop, Tooltip } from 'antd';
import { PlayCircleOutlined, HeartOutlined } from '@ant-design/icons';
import { ha, ISong } from '../../http/cloudMusic'
import { formatPicUrl, formatDuration } from '../../utils/format'

export default function Page({ children, location, route, history, match }: IRouteComponentProps) {
  const [data, setData] = useState(new Array<ISong>());
  const [loading, setLoading] = useState(false);
  const { id } = location.query


  const columns: ColumnsType<ISong> = [
    {
      key: 'index',
      title: '序号',
      align: 'center',
      width: 80,
      render: (_, record, index) => (<span>{index}</span>),
    },
    {
      key: 'action',
      title: '操作',
      align: 'center',
      width: 100,
      render: (_, record, index) => (
        <Space>
          <Tooltip title="喜欢">
            <HeartOutlined onClick={() => favoriteClick(record.id)} />
          </Tooltip>
          <Tooltip title="播放">
            <PlayCircleOutlined onClick={() => playClick(index)} />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '音乐名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '演唱者',
      dataIndex: 'singer',
      key: 'singer',
      ellipsis: true,
    },
    {
      title: '专辑',
      dataIndex: 'album',
      key: 'album',
      ellipsis: true,
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      align: 'center',
    },
  ];



  useEffect(() => {
    // console.log(id)
    setLoading(true)
    ha.neteaseCloudMusic(`/playlist/track/all?id=${id}`).then(res => {
      let arr = res.songs.map((ele: any) => {
        const { id, name, al, ar } = ele
        return {
          id,
          name,
          singer: ar[0].name,
          album: al.name,
          picUrl: formatPicUrl(al.picUrl),
          duration: formatDuration(ele.dt)
        } as ISong
      })
      setData(arr)
    }).finally(() => {
      setLoading(false)
    })

    return () => {
      console.log('unmount')
    }
  }, [])


  const favoriteClick = (id: number) => {
    console.log(id)
  }

  // 播放
  const playClick = (index: number) => {
    ha.cloudMusicApi({ act: 'playlist', id, index }).then(({ code, msg }) => {
      message.info(msg);
    })
  }

  // 播放全部
  const playAllClick = () => {
    ha.cloudMusicApi({ act: 'playlist', id }).then(({ code, msg }) => {
      message.info(msg);
    })
  }

  return (
    <>
      <Table bordered={true}
        loading={loading}
        rowKey={record => record.id}
        title={() => (<Button type="primary" icon={<PlayCircleOutlined />} onClick={playAllClick}>播放全部</Button>)}
        columns={columns}
        size={'small'}
        pagination={{ hideOnSinglePage: true, defaultPageSize: 10000 }} dataSource={data} />
    </>
  );
}
