import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardSummary } from "../../types/dashboard";

export default function RunTrendChart({ data }: { data: DashboardSummary["trend"] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ left: -12, right: 12, top: 12, bottom: 4 }} barCategoryGap="38%">
          <CartesianGrid stroke="rgba(203, 213, 225, 0.14)" strokeDasharray="3 5" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: "#aab4c0" }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: string) => value.slice(5)}
            tickMargin={12}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#aab4c0" }}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
            width={36}
            tickMargin={8}
          />
          <Tooltip
            cursor={{ fill: "rgba(203, 213, 225, 0.06)" }}
            contentStyle={{ background: "#202329", border: "1px solid rgba(203, 213, 225, 0.18)", borderRadius: 10, color: "#f3f4f6", boxShadow: "0 12px 28px rgba(0,0,0,.3)" }}
            labelStyle={{ color: "#aab4c0", marginBottom: 6 }}
            itemStyle={{ color: "#f3f4f6", padding: "2px 0" }}
            labelFormatter={(value) => `Date · ${value}`}
            formatter={(value: number, name: string) => [value, name]}
          />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ paddingTop: 18, color: "#c5ccd5", fontSize: 12 }} />
          <Bar dataKey="passed" name="Passed" stackId="a" fill="#25a58d" />
          <Bar dataKey="failed" name="Failed" stackId="a" fill="#ed6257" />
          <Bar dataKey="review" name="Needs review" stackId="a" fill="#e3a33d" />
          <Bar dataKey="errors" name="Errors" stackId="a" fill="#8b95a5" />
          <Bar dataKey="pending" name="Pending" stackId="a" fill="#cbd5e1" radius={[5, 5, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
