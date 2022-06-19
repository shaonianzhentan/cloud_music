import { IRouteComponentProps } from 'umi'
import React, { useState } from 'react';
import styles from './radio.less';
import globalStyles from '../../style/global.less'
import { Card, List } from 'antd';
import { cloudMusicFetch, IPersonalized } from '../../http/cloudMusic'
import { formatPicUrl } from '../../utils/format'
const { Meta } = Card

let data = new Array<IPersonalized>();

cloudMusicFetch('/personalized/djprogram').then(res => {
  data = res.result
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
            <Meta className={globalStyles.meta} title={item.name} />
          </Card>
        </List.Item>
      )}
    />
  );
}