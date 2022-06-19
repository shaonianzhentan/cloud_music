import { IRouteComponentProps } from 'umi'
import React, { useState } from 'react';
import styles from './singer.less';
import globalStyles from '../../style/global.less'
import { Card, List } from 'antd';
import { cloudMusicFetch, IArtists } from '../../http/cloudMusic'
import { formatPicUrl } from '../../utils/format'
const { Meta } = Card

let data = new Array<IArtists>();

cloudMusicFetch('/toplist/artist?type=1').then(res => {
  data = res.list.artists
})

export default function Page({ history }: IRouteComponentProps) {
  return (
    <List
      grid={{ gutter: 8, column: 5 }}
      dataSource={data}
      renderItem={item => (
        <List.Item>
          <Card hoverable cover={<img src={formatPicUrl(item.picUrl)} />}
            onClick={() => history.push(`/player/playlist?id=${item.id}`)}>
            <Meta className={styles.meta} title={item.name} />
          </Card>
        </List.Item>
      )}
    />
  );
}