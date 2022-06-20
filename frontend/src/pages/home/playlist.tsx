import { IRouteComponentProps } from 'umi'
import React, { useState, useEffect } from 'react';
import styles from './playlist.less';
import globalStyles from '../../style/global.less'
import { Card, List } from 'antd';
import { ha, IPersonalized } from '../../http/cloudMusic'
import { formatPicUrl } from '../../utils/format'

const { Meta } = Card


export default function Page({ history }: IRouteComponentProps) {

  const [data, setData] = useState<Array<IPersonalized>>([])
  useEffect(() => {

    ha.neteaseCloudMusic('/personalized').then(res => {
      setData(res.result)
    })

    return () => {

    }
  }, [])


  return (
    <List
      grid={{ gutter: 8, column: 5 }}
      dataSource={data}
      renderItem={item => (
        <List.Item>
          <Card hoverable cover={<img src={formatPicUrl(item.picUrl)} />}
            onClick={() => history.push(`/player/playlist?id=${item.id}`)}>
            <Meta className={globalStyles.meta} title={item.name} />
          </Card>
        </List.Item>
      )}
    />
  );
}