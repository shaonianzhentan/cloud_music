import { IRouteComponentProps } from 'umi'
import React, { useEffect, useState } from 'react';
import styles from './playlist.less';
import type { ColumnsType } from 'antd/lib/table';
import { Card, Space, Button, Table, message } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import { cloudMusicFetch, ISong, cloudMusicPost } from '../../http/cloudMusic'
import { formatPicUrl, formatDuration } from '../../utils/format'

const columns: ColumnsType<ISong> = [
  {
    title: '序号',
    key: 'index',
    align: 'center',
    width: 80,
    render: (_, record, index) => (<span>{index}</span>),
  },
  {
    title: '操作',
    key: 'action',
    align: 'center',
    width: 100,
    render: (_, record) => (
      <a>喜欢</a>
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

export default function Page({ children, location, route, history, match }: IRouteComponentProps) {
  const [data, setData] = useState(new Array<ISong>());
  const [loading, setLoading] = useState(false);
  const { id } = location.query
  useEffect(() => {
    // console.log(id)
    setLoading(true)
    cloudMusicFetch(`/playlist/track/all?id=${id}`).then(res => {
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


  // 播放全部
  const playAll = () => {
    cloudMusicPost({
      act: 'playlist',
      id
    }).then(({ code, msg }) => {
      message.info(msg);
    })
  }

  return (
    <Table bordered={true}
      loading={loading}
      title={() => (<Button type="primary" icon={<PlayCircleOutlined />} onClick={playAll}>播放全部</Button>)}
      columns={columns}
      size={'small'}
      pagination={{ hideOnSinglePage: true, defaultPageSize: 10000 }} dataSource={data} />
  );
}
