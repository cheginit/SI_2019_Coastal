module discharge_module
    implicit none

    logical, save :: setup = .false.

    contains

    subroutine setup_discharge(velocity, x_r1, x_r2)
        real(kind=8), intent(in out) :: velocity, x_r1, x_r2

        integer :: iunit, istat
        logical :: foundFile
        character(len=255) :: q_input
        real(kind=8) :: inputs(3)

        if (.not. setup) then
            iunit = 40

            q_input = '../discharge.data'

            inquire(file=trim(adjustl(q_input)), exist=foundFile)
            if (.not. foundFile) then
              write(*,*) 'Missing discharge data file ...'
              write(*,*) 'Looking for ', trim(adjustl(q_input)),' file'
              stop
            endif

            open(iunit, file=trim(adjustl(q_input)), status='old', iostat=istat)

            rewind(iunit)
            read(iunit, *, iostat=istat) inputs(:)

            velocity = inputs(1)
            x_r1 = inputs(2)
            x_r2 = inputs(3)

            close(unit=iunit, iostat=istat)

            setup = .true.
        end if

    end subroutine setup_discharge
end module discharge_module
