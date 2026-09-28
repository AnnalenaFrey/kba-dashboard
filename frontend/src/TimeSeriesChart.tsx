import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart} from 'recharts';
import type { TimeSeriesEntry } from './types';


export default function TimeSeriesChart( {data}: {data:TimeSeriesEntry[]} ) {

    const chartData = data.map((entry) => ({...entry, label: `${entry.year}-${entry.month}`})).reverse();
    return (
        <LineChart
        style={{ width: '100%', maxWidth: 900, aspectRatio: 1.618 }}
        
        data={chartData}
        margin={{
            top: 20,
            right: 20,
            left: 0,
            bottom: 5,
        }}
        >
        <CartesianGrid strokeDasharray="5 5"/>
        <XAxis dataKey="label" interval={0} tick={{fontSize: 12}} />
        <YAxis width="auto" tick={{fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Line dataKey="total_car_registrations" type={'monotone'} strokeWidth={2} />
        </LineChart>
    );
    }