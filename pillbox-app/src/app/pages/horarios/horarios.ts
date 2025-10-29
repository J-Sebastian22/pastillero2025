import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Horario } from '../../services/horario';
import { Medicamento } from '../../services/medicamento';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-horarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './horarios.html',
  styleUrl: './horarios.css'
})
export class Horarios {
horarios: any[] = [];
  medicamentos: any[] = [];
  nuevoHorario = { id_medicamento: '', hora_toma: '', frecuencia: '' };
  usuario: any;

  constructor(
    private horarioService: Horario,
    private medicamentoService: Medicamento,
    private auth: Auth
  ) {}

  ngOnInit() {
    this.usuario = this.auth.obtenerUsuario();
    if (this.usuario) {
      this.cargarMedicamentos();
      this.cargarHorarios();
    }
  }

  cargarMedicamentos() {
    this.medicamentoService.getByUsuario(this.usuario.id).subscribe({
      next: (data: any) => this.medicamentos = data,
      error: (err: any) => console.error(err)
    });
  }

  cargarHorarios() {
    this.horarioService.getByUsuario(this.usuario.id).subscribe({
      next: (data: any) => this.horarios = data,
      error: (err: any) => console.error(err)
    });
  }

  agregarHorario() {
    if (!this.nuevoHorario.id_medicamento || !this.nuevoHorario.hora_toma) return;

    this.horarioService.create(this.nuevoHorario).subscribe({
      next: () => {
        this.cargarHorarios();
        this.nuevoHorario = { id_medicamento: '', hora_toma: '', frecuencia: '' };
      },
      error: (err: any) => console.error(err)
    });
  }

  eliminarHorario(id: number) {
    this.horarioService.delete(id).subscribe({
      next: () => this.cargarHorarios(),
      error: (err: any) => console.error(err)
    });
  }
}
