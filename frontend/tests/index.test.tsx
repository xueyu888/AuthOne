import { render, screen, fireEvent } from '@testing-library/react';
import IndexPage from '../pages/index';

// 禁用真实网络请求，确保测试不会调用后端
jest.mock('axios', () => ({
  post: jest.fn().mockResolvedValue({ data: {} })
}));

describe('IndexPage', () => {
  it('renders create role form and updates input', () => {
    render(<IndexPage />);
    // 检查标题存在
    expect(screen.getByText('AuthOne 管理控制台')).toBeInTheDocument();
    // 检查角色表单
    const input = screen.getByPlaceholderText('角色名称') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'admin' } });
    expect(input.value).toBe('admin');
  });
});