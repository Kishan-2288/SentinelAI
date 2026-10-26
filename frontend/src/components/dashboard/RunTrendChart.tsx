import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardSummary } from "../../types/dashboard";

export default function RunTrendChart({ data }: { data: DashboardSummary["trend"] }) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ left: -16, right: 8, top: 8 }}>
          <CartesianGrid stroke="#d9dfdc" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: "#5b6b78" }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: string) => value.slice(5)}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#5b6b78" }}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
            label={{ value: "Cases", angle: -90, position: "insideLeft", fill: "#5b6b78", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ fill: "#f2f4f3" }}
            labelFormatter={(value) => `Date: ${value}`}
            formatter={(value: number, name: string) => [value, name]}
          />
          <Legend iconType="square" />
          <Bar dataKey="passed" name="Passed" stackId="a" fill="#0f6b5c" />
          <Bar dataKey="failed" name="Failed" stackId="a" fill="#b3261e" />
          <Bar dataKey="review" name="Needs review" stackId="a" fill="#c47f17" />
          <Bar dataKey="errors" name="Errors" stackId="a" fill="#6b7280" />
          <Bar dataKey="pending" name="Pending" stackId="a" fill="#cbd5e1" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
